import os
import storage

HIDE_DRIVE_FILE_PATH = "remove_to_hide_drive.txt"


def hide_drive_file_exists() -> bool:
	file_exists = HIDE_DRIVE_FILE_PATH in os.listdir("/")	
	if file_exists:
		print(f"File '{HIDE_DRIVE_FILE_PATH}' does exist.")
	else:
		print(f"Could not find file: {HIDE_DRIVE_FILE_PATH}")
	return file_exists


def write_hide_drive_file() -> bool:
	try:
		with open(HIDE_DRIVE_FILE_PATH, "w") as filehandler:
			print("Remove this file to hide usb drive.")
			filehandler.close()
		return True
	except Exception as e:
		print(f"Could not write '{HIDE_DRIVE_FILE_PATH}': {e}")
		return False


def remount_drive_writable() -> None:
	""" This makes the usb drive only writable for the microcontoller. """
	storage.remount("/", False)
	print("Made the file system writable.")
