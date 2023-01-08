#!/usr/bin/env bash
set -euo pipefail

PATH_USB_DRIVE="/run/media/jni/CIRCUITPY1"

# Exit if root
if [ "$EUID" -eq 0 ]
  then echo "Please do not run as root"
  exit
fi

# Helper function to ask a yes/no question
question_yes_no() {
	local question="$1"
	local answer
	while true; do
		read -p "$question [Y/n] " answer
		case $answer in
			[Yy]* ) return 0;;
			[Nn]* ) return 1;;
			* ) return 0;;
		esac
	done
}

# This will check for `remove_to_hide_drive.txt` file which is a good indicator
# for operating with the keyboard's USB drive.
if [ -f "${PATH_USB_DRIVE}/remove_to_hide_drive.txt" ]; then
	echo "ERROR: USB drive from keyboar selected!"
	echo "Check the 'PATH_USB_DRIVE' variable at the top of this script."
	echo "Current value: ${PATH_USB_DRIVE}"
	exit 1
else
	echo "Correct USB drive found at: ${PATH_USB_DRIVE}"
fi

if ! question_yes_no "Updating code.py, and JNI files on device?"; then
	echo "Not updating. Will exit."
	exit 0
fi

echo "Removing old files..."
rm -fv "${PATH_USB_DRIVE}/code.py"
find "${PATH_USB_DRIVE}" ! -name "jni_secrets.py" -name "jni_*.py" -delete -print

echo "Copying new files..."
cp -v ./code.py "${PATH_USB_DRIVE}/code.py"
find . -name "jni_*.py" -exec cp {} "${PATH_USB_DRIVE}" \; -print

exit 0