# Enrollment Bot

A scripting tool to automatically enroll on UCSD WebReg.

_Note: For systems with Python 2 only, for Python 3 go [here](https://github.com/cpacker/enrollment-bot)_

## Requirements and Dependencies
- Python 2.x (get it [here](https://www.python.org/downloads/))
- Libraries `mechanize` and `cookielib`

## Usage and Installation

### How to install
1. Download or clone the python2 branch of the project (`git clone -b python2 https://github.com/cpacker/enrollment-bot.git`)
2. Install the project dependencies (see below)

##### If you have root access to your machine:
- Python modules `mechanize` and `cookielib`. Install them with:
```
pip install mechanize
pip install cookielib
```
- You may have to use `sudo pip install`

##### If you do not have root access, or if you'd rather supply the dependencies locally:
##### Mechanize:
- Go to the [mechanize](https://github.com/jjlee/mechanize) repository page and select `Download as ZIP`
- Move the folder `mechanize` inside the unzipped `mechanizemaster` folder you just downloaded into the project directory (`enrollment-bot/`)

##### Cookielib:
- Download the cookielib.py file [here](https://hg.python.org/cpython/raw-file/b617790557b3/Lib/cookielib.py) and move it to the project directory

### How to configure
Modify `PID`, `PASS` and `SECTION_IDS` in `settings.py` to be your PID, password and a list of valid section IDs from WebReg
```python
# Authentication Settings
PID = 'A12345678' # change this to your PID
PASS = 'ilovepugs5' # change this to your SSO password

# Enrollment Options
SECTION_IDS = ['843721','939283','422304'] # change these to the section IDs you want to add
```

### How to use
- To execute the script directly, simply run `python regbot.py` from the project directory
- If you would like to have the script execute at a certain time, you can use the Unix utility `at`. 
- For example, the following will run enrollment-bot at 9PM today, or tomorrow if it is already past 9PM:
```bash
# Run this from the project directory!
echo "python regbot.py" | at 2100
```
- For more information on how to use `at`, visit [this](https://kb.iu.edu/d/aewo) website

_Your computer needs to be on at the given time for `at` to run enrollment-bot. Instead, use `at` on a server you know will be running at when your enrollment time starts._

Running on ieng6.ucsd.edu:
- ieng6 has Python 2 installed by default
- ieng6 will automatically send you the output of your job via email, so check your email to see the terminal output
- A copy of the terminal/debug output will also be saved to `log.log` in the project directory

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## License

Distributed under the MIT license.

## Disclaimer
- For educational purposes only: I do not condone the use of this script on actual university services
- *Use at your own risk!*

## To-do
- ~~Built-in SMTP mailer to send status update on completion / failure~~ ieng6 automatically does this when you use `at`
