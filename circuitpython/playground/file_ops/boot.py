import time
import board
import digitalio
import storage

pin_read = digitalio.DigitalInOut(board.A0)
pin_read.direction = digitalio.Direction.INPUT
pin_read.pull = digitalio.Pull.UP

print("Checking for A0 pin to be grounded to make the filesystem writeable.")
GROUNDED_YES = False
GROUNDED_NO = True

if pin_read.value is GROUNDED_YES:
	print("A0 pin is grounded!")
	storage.remount("/", False)
	print("Making the file system writable.")
else:
	print("A0 pin is not grounded.")
	print("Filesystem will stay readonly.")
time.sleep(0.5)
