import time
import os
import storage

CALIB_FILEPATH = "joy_fw_calibration.txt"
print(f"Checking for file '{CALIB_FILEPATH}' to make the filesystem writeable if not present.")

root_content = os.listdir("/")
if CALIB_FILEPATH in root_content: 
	print("Calibration file is present.")
else:
	print(f"Could not find '{CALIB_FILEPATH}'")
	print("Making the file system writable.")
	storage.remount("/", False)
	time.sleep(0.5)
	print("Filesystem is writeable to store new calibration.")
