# README


## Description
This script will help configure the Zymbit module and the host pi to be secure and production ready. This will put the Zymbit module in production mode, set self-destruct policy for tamper detect, and load theessential boot files for verified boot process. This will also sanitize the host device by mounting read-only filesystem, gen random strong passwords using pwgen for all /bin/bash users, disable root account login, disable SSH, andremove remote applications: CURL, WGET, GCC, APT, DPKG.

## Warning
This script disables/deletes many essential features. Make sure the device is ready for production release before the script is called to lockdown the host.

## Usage
This script must be run with sudo. sudo ./host_security_sanitization.py 
The script will simply prompt the user for a (Y/n) for each feature. Destructive features will prompt (Y/n) twice to make sure the user understands it's destructive.

Example usage:
```
>>>sudo ./host_security_sanitization.py
>>>Load file manifest (Alpha edition) (Y/n): n
>>>Set perimeter events to self-destruct (Y/n): n
>>>Set bind lock? (Warning! permanent) (Y/n): n
>>>Mount filesystem persistently as read-only on next boot (Y/n): n
>>>Generate random strong passwords for user accounts using pwgen (Y/n): n
>>>Remove CURL, WGET, GCC, APT, DPKG? (Y/n): y
>>>Disable root account login? (Y/n): n
>>>Disable SSH (Y/n): n
>>>Warning! Are you sure you want to uninstall CURL? (Y/n): n
>>>Warning! Are you sure you want to uninstall WGET? (Y/n): n
>>>Warning! Are you sure you want to uninstall GCC? (Y/n): y
>>>Removing GCC...
>>>Done!

>>>Warning! Are you sure you want to uninstall APT? (Y/n): n
>>>Warning! Are you sure you want to uninstall DPKG? (Y/n): n
```



## License
 Copyright (C) 2022 by copyright Zymbit

 Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without l> imitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
