import time
import board
import digitalio

pin_read = digitalio.DigitalInOut(board.A0)
pin_read.direction = digitalio.Direction.INPUT
pin_read.pull = digitalio.Pull.UP

print("Ground or not ground pin 'A0'")
GROUNDED_YES = False
GROUNDED_NO = True

while True:
	if pin_read.value is GROUNDED_YES:
		print("A0 pin is grounded!")
	else:
		print("A0 pin is not grounded.")
	time.sleep(0.5)
