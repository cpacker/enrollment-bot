# Enrollment Bot

A scripting tool to automatically enroll on UCSD WebReg.

_Note: Tested on Python 2.7.6 only, Python 3 support coming shortly_

## Requirements
- The OSX or Linux terminal app / BASH
- Python 2.x (get it [here](https://www.python.org/downloads/))
- Python modules `mechanize` and `cookielib`. Install them with:
```
pip install mechanize
``` 
```
pip install cookielib
```
- You may have to use `sudo pip install`


## Usage and Installation
1. Download or clone the project
2. Navigate to the project directory
3. Modify `PID`, `PASS` and `SECTION_IDS` in `regbot.py` to be your PID, password and a list of valid section IDs from WebReg
```python
# User settings
PID = 'A12345678' # change this to your PID
PASS = 'supersecret' # change this to your SSO password
SECTION_IDS = ['843721','939283','422304'] # change these to the classes you want to add
```
4. `chmod +x enroll` to make the script executable
5. `./enroll` to launch the script

A copy of the terminal output will be saved to `log.txt` in the project directory


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
