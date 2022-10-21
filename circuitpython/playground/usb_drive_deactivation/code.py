import time
import board
import neopixel
import storage
from digitalio import DigitalInOut, Pull


def main():
	BUTTON_IS_PRESSED = False	
	int_button = DigitalInOut(board.IO0)
	int_button.switch_to_input(pull=Pull.UP) 

	GREEN = (0, 255, 0)
	RED = (255, 0, 0)
	START = (0, 206, 209)
	BLACK = (0, 0, 0)

	pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
	pixel.brightness = 0.3
	pixel.fill(START)
	
	hide_drive = True
	counter = 0
	while counter < 30:
		time.sleep(0.1)	
		counter += 1
		if BUTTON_IS_PRESSED == int_button.value:
			print("Will show drive...")
			pixel.fill(GREEN)
			time.sleep(1)
			hide_drive = False
			counter = 30
	if hide_drive:
		print("Will not show drive")
		pixel.fill(RED)
		# This will only work when this file is copied as 'boot.py' to the USB drive.
		# In case you end up in an infinite loop use 'safe mode' to avoid starting boot.py
		# Safe mode for FeatherS3:
		# - 1. Press the [RESET] button to reset the ESP32-S3 chip
		# - 2. After the RGB LED has gone purple and then off, 
		#      press and hold the [BOOT] button for a few seconds
		storage.disable_usb_drive()
		time.sleep(1)
	pixel.fill(BLACK)


if __name__ == "__main__":
	main()
