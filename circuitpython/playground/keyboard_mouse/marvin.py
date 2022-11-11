# circup install adafruit_hid
import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


def main():
	keyboard = Keyboard(usb_hid.devices)  # type: ignore
	layout = KeyboardLayoutUS(keyboard)
	keyboard.press(Keycode.COMMAND, Keycode.SPACEBAR)
	keyboard.release_all()

	layout.write("messages")
	time.sleep(1)

	keyboard.press(Keycode.ENTER)
	keyboard.release_all()
	time.sleep(1)

	keyboard.press(Keycode.COMMAND, Keycode.N)
	keyboard.release_all()

	time.sleep(0.5)
	layout.write("nixdorf")
	time.sleep(0.5)

	keyboard.press(Keycode.TAB)
	keyboard.release_all()
	time.sleep(0.5)

	layout.write("Hello")
	keyboard.press(Keycode.ENTER)
	keyboard.release_all()
	time.sleep(0.5)

	keyboard.press(Keycode.COMMAND, Keycode.Q)
	keyboard.release_all()


if __name__ == "__main__":
	main()
