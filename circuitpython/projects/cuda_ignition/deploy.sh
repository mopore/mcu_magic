#!/usr/bin/env bash
set -euo pipefail

PATH_USB_DRIVE="/run/media/jni/CIRCUITPY1"

MPY_CROSS_COMMAND="mpy-cross-7.3.3"

# If mpy-cross command is availale
if ! command -v "$MPY_CROSS_COMMAND" &> /dev/null
then
	echo "ERROR: Command '$MPY_CROSS_COMMAND' not available in path."
	exit 9
fi


# Exit if root
if [ "$EUID" -eq 0 ]
  then echo "Please do not run as root"
  exit 9
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
	echo "ERROR: Found keyboard!"
	echo "Check the 'PATH_USB_DRIVE' variable at the top of this script."
	echo "Current value: ${PATH_USB_DRIVE}"
	exit 1
else
	echo "Target drive found at: ${PATH_USB_DRIVE}"
fi

if ! question_yes_no "Updating code.py, boot.py and JNI files on device?"; then
	echo "Not updating. Will exit."
	exit 0
fi

echo "Removing old files..."
rm -fv "${PATH_USB_DRIVE}/code.py"
rm -fv "${PATH_USB_DRIVE}/boot.py"
# Delete old files other than jni_secrets.py
find "${PATH_USB_DRIVE}" ! -name "jni_secrets.py" -name "jni_*.mpy" -delete -print

echo "Copying new files..."
cp -v ./code.py "${PATH_USB_DRIVE}/code.py"
if [ -f ./boot.py ]; then
	cp -v ./boot.py "${PATH_USB_DRIVE}/boot.py"
fi
# Precomile and copy new files
find . -name "jni_*.py" -exec mpy-cross-7.3.3 {} \; -print
find . -name "jni_*.mpy" -exec mv {} "${PATH_USB_DRIVE}" \; -print

exit 0