import time
import board
import neopixel
import storage
import microcontroller
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
	
	use_safe_mode = False
	counter = 0
	while counter < 30:
		time.sleep(0.1)	
		counter += 1
		if BUTTON_IS_PRESSED == int_button.value:
			print("Will reset to safe mode...")
			pixel.fill(GREEN)
			time.sleep(1)
			use_safe_mode = True
			counter = 30
	if use_safe_mode:
		print("Will reset to safe mode")
		microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
		microcontroller.reset()
	else:
		while True:
			pixel.fill(RED)
			time.sleep(0.5)
			pixel.fill(BLACK)
			time.sleep(0.5)


if __name__ == "__main__":
	main()
