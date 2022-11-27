import hide_drive
import storage


def main() -> None:
	file_exists = hide_drive.hide_drive_file_exists()
	if not file_exists:
		# Normal mode
		hide_drive.remount_drive_writable()  # Will be writable for microcontroller only
		storage.disable_usb_drive()
	# else:  USB Drive is visible and writable from PC


if __name__ == "__main__":
	main()
