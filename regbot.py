#!/usr/bin/python
import mechanize
import cookielib

# QUARTER = 'SP15' # quarter by shorthand
# REGISTRATION_LEVEL = 'UN' # default, other options GR (grad), PH (pharm)
SECTION_IDS = ['SECTION_ID_NUMBER','839547','839480','839480']


# ------------------------------------- #
#           Setup Environment           #
# ------------------------------------- #

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
br.set_handle_gzip(True)
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
br.form['urn:mace:ucsd.edu:sso:username'] = raw_input("Enter your PID: ")
br.form['urn:mace:ucsd.edu:sso:password'] = raw_input("Enter your password: ")
# Attempt to log in with credentials
br.submit()
login_response_text = br.response().read()

# Raise error if credentials are incorrect
if 'Login failed' in login_response_text:
    print 'ERROR: Could not login with given credentials'

# Since we do not have javascript enabled, we must click continue to proceed
br.select_form(nr=0)
br.submit()


# ------------------------------------- #
#      Enrollment Selection Page        #
# ------------------------------------- #

print 'Attempting to select an enrollment period'
# TODO: Raise error on enrollment fail
# Select an enrollment period
br.select_form(nr=0)
# By not changing form defaults we automatically choose the current quarter
# br.form['reg_term'] = QUARTER
# br.form['reg_lvl'] = REGISTRATION_LEVEL
br.submit()


# ------------------------------------- #
#         WebReg Enrollment Page        #
# ------------------------------------- #

section_ids = SECTION_IDS

# Go through all the section IDs and attempt to add or waitlist the classes
for s_id in section_ids:
    # Section ID form on webreg
    br.select_form(nr=1)
    # Input the section ID and submit
    br.form['secid'] = s_id
    print 'Attempting to add section ID: ' + s_id
    br.submit()
    add_response_text = br.response().read()

    #=== Handle Response Page ===#
    # Case 0: The section ID does not correspond to a correct class
    if 'Request Unsuccessful' in add_response_text:
        print 'ERROR: Could not add section ID ' + s_id
        # Form nr=0 is the 'Return to WebReg Enrollment Page'
        print 'Returning to WebReg enrollment page'
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
            print 'ERROR: Could not add section ' + s_id
        # Case 1: We successfully add the class
        elif 'Request Successful' in confirm_response_text: 
            print 'Successfully added section ' + s_id
        # Case 2: (?) Did not land on a "Request Successfull" page
        else:
            print 'ERROR: Did not get success message after add'
        # Form nr=0 is the 'Return to WebReg Enrollment Page'
        print 'Returning to WebReg enrollment page'
        br.select_form(nr=0)
        br.submit()

print 'Done.'
