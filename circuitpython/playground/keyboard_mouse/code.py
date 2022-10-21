# circup install adafruit_hid
import time
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


def main():
	mouse = Mouse(usb_hid.devices)

	print("Testing mouse...")
	mouse.move(x=300)
	time.sleep(1)
	mouse.move(x=-600)
	# Other available options...
	# mouse.press(Mouse.LEFT_BUTTON) or mouse.release(Mouse.LEFT_BUTTON)
	# mouse.move(wheel=-200)
	print("Testing keyboard...")
	keyboard = Keyboard(usb_hid.devices)
	layout = KeyboardLayoutUS(keyboard)
	layout.write("Hello World!")
    # Testing Keyboard Combo
	#  keyboard.press(Keycode.SHIFT, Keycode.A)
	#  keyboard.release_all()
	print("All done...")
	

if __name__ == "__main__":
	main()
