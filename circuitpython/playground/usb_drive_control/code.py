import time
import hide_drive
import microcontroller

# Given that all three files in this directory are copied to the microcontroller the usb drive
# will not show up after start until a file 'remove_to_hide_drive.txt' is present in the drive's 
# root directory.
# Such a file will be automatically written after 20 seconds if it does not exist. The 
# microcontroller will then reset.
# After the reset the usb boot drive will show up and will be writable for the PC.


def main() -> None:

	hide_drive_file_exists = hide_drive.hide_drive_file_exists()
	if not hide_drive_file_exists:
		# The following testing code will write make the flash usable/visable again...
		print("Hide drive does not exist and will be written in 20 seconds...")
		time.sleep(15)
		print("Hide drive file will be written in 5 seconds...")
		time.sleep(5)
		file_written = hide_drive.write_hide_drive_file()
		if file_written:
			print("File successfully written...")
			time.sleep(1)
			print("Resetting microcontroller...")
			microcontroller.reset()  # type: ignore
		else:
			print("Could not write file. Already in Debug mode?")


if __name__ == "__main__":
	main()
