import mechanizepython3
import cookiejar
import logging
import time
from datetime import datetime
import settings

'''
Disclaimer:
For education purposes only
I do not condone the use of this script on actual university services
!!! Use at your own risk !!!
'''


# ===================================== #
#          Program Settings             #
#          * Do not modify *            #
# ===================================== #

# Setup the logger
logging.basicConfig(filename='log.log',level=logging.DEBUG)
# Setup console output
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


# Number of times to try enrolling after failure before exiting program
ATTEMPT = 5

# Error code constants
SUCCESS      = 0
# Application errors:
AUTH_ERROR   = 1
SELECT_ERROR = 2
ENROLL_ERROR = 3

def print_error(flag):
    if flag == AUTH_ERROR:
        logging.error('An error occured during authentication. Make sure your PID and password are correctly setup.')
    elif flag == SELECT_ERROR:
        logging.error('An error occured while trying to select an enrollment time.')
    elif flag == ENROLL_ERROR:
        logging.error('An error occured while trying to add a class. Make sure your section IDs are correct.')


# =================================================================#
#  enroll():                                                       #
#    Main function that creates a browser object and attempts      #
#    to navigate through pages on WebReg and automate enrollment   #
#                                                                  #
#  Return values:                                                  #
#    Function returns a status code upon completion or             #
#    premature exit                                                #
#    If the browser is able to correctly navigate the webpages     #
#    and select / submit forms, then we can expect the following   #
#    errors:                                                       #
#      AUTH_ERROR:   Could not login through SSO with the          #
#                    supplied credentials                          #
#      SELECT_ERROR: Could not proceed past enrollment period      #
#                    selection page, most likely due to running    #
#                    the script when a user's enrollment is closed #
#      ENROLL_ERROR: Could not add the class corresponding to a    #
#                    provided section ID, either because the       #
#                    section ID is incorrect, or because the class #
#                    cannot be added for some other reason eg.     #
#                    maximum units exceeded                        #
# =================================================================#

def enroll():
    # ------------------------------------- #
    #           Setup Environment           #
    # ------------------------------------- #

    # Status flag to return at end
    ERROR_FLAG = SUCCESS

    # Browser
    br = mechanize.Browser()
    # Debug options:
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    # br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # User-Agent
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    # Go to Webreg URL, will prompt SSO sign-on page
    r = br.open('https://act.ucsd.edu/cgi-bin/tritonlink.pl/8/students/academic/classes/acd/webregR.pl')


    # ------------------------------------- #
    #        SSO Authentication Page        #
    # ------------------------------------- #

    # Submit SSO authentication
    br.select_form(nr=0)
    br.form['urn:mace:ucsd.edu:sso:username'] = settings.PID
    br.form['urn:mace:ucsd.edu:sso:password'] = settings.PASS
    # Attempt to log in with credentials
    br.submit()
    login_response_text = br.response().read()

    # Raise error if credentials are incorrect
    if 'Login failed' in login_response_text:
        logging.error('Could not login with given credentials')
        return AUTH_ERROR

    # Since we do not have javascript enabled, we must click continue to proceed
    br.select_form(nr=0)
    br.submit()


    # ------------------------------------- #
    #      Enrollment Selection Page        #
    # ------------------------------------- #

    logging.debug('Attempting to select an enrollment period')
    # Select an enrollment period
    br.select_form(nr=0)
    # By not changing form defaults we automatically choose the current quarter
    # br.form['reg_term'] = QUARTER
    # br.form['reg_lvl'] = REGISTRATION_LEVEL
    br.submit()

    # # TODO: Raise error on enrollment time select fail
    # select_period_response_text = br.response().read()
    # # print select_period_response_text
    # if 'TODO' in select_period_response_text:
    #     return SELECT_ERROR


    # ------------------------------------- #
    #         WebReg Enrollment Page        #
    # ------------------------------------- #

    section_ids = settings.SECTION_IDS

    # Go through all the section IDs and attempt to add or waitlist the classes
    for s_id in section_ids:
        # Section ID form on webreg
        br.select_form(nr=1)
        # Input the section ID and submit
        br.form['secid'] = s_id
        logging.debug('Attempting to add section ID: ' + s_id)
        br.submit()
        add_response_text = br.response().read()

        #=== Handle Response Page ===#
        # Case 0: The section ID does not correspond to a correct class
        if 'Request Unsuccessful' in add_response_text:
            logging.error('Could not add section ID ' + s_id)
            ERROR_FLAG = ENROLL_ERROR
            # Form nr=0 is the 'Return to WebReg Enrollment Page'
            logging.debug('Returning to WebReg enrollment page')
            br.select_form(nr=0)
            br.submit()
        # Case 1: The class exists
        else:
            #=== Attempt to add the class ===#
            # If the class is waitlisted, then nr=0 is the waitlist submit form
            # If the class is NOT waitlisted, the nr=0 is the normal submit form
            # Either way, selecting nr=0 and submitting will try to add or waitlist the class
            br.select_form(nr=0)
            br.submit()
            confirm_response_text = br.response().read()

            #=== Handle Response Page ===#
            # Case 0: We exceed maximum units
            if 'Request Unsuccessful' in confirm_response_text:
                logging.error('Could not add section ' + s_id)
                ERROR_FLAG = ENROLL_ERROR
            # Case 1: We successfully add the class
            elif 'Request Successful' in confirm_response_text: 
                logging.info('Successfully added section ' + s_id)
            # Case 2: (?) Did not land on a "Request Successfull" page
            else:
                logging.error('Did not get success message after add')
                ERROR_FLAG = ENROLL_ERROR
            # Form nr=0 is the 'Return to WebReg Enrollment Page'
            logging.debug('Returning to WebReg enrollment page')
            br.select_form(nr=0)
            br.submit()

    return ERROR_FLAG


# Driver function that accounts for potential exceptions from network errors
# Returns SUCCESS on success and an error code otherwise
def run_driver():
    try:
        # Run the main script
        status = enroll()
        # Check for expected errors and complete
        if (status != SUCCESS):
            print_error(status)
        else:
            logging.debug('Successfully enrolled on attempt ' + str(attempts))
        return status

    except Exception as e:
        # If a network / browser error occured, catch it and report the code
        logging.debug(e)
        logging.error('An unexpected error occured while trying to run the program.')
        return -1

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["password"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

# Entry point of script
# Calls the driver function until success ATTEMPT number of times 
if __name__ == '__main__':
    attempts = 0
    while (attempts < ATTEMPT):
        logging.debug('[ Attempt ' + str(attempts+1) + ': ' + str(datetime.now()) + ' ]')
        status = run_driver()
        if (status == SUCCESS):
            break
        else:
            attempts += 1
            time.sleep(1) # Delay a second before trying again

    # TODO mail status at end
    if (status == SUCCESS):
        # mail(SUCCESS)
        logging.info('Completed successfully.')
    else:
        # mail(FAILURE)
        logging.info('Program exited with errors.')
