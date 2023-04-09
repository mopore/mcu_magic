import board
import displayio
import terminalio

import adafruit_displayio_sh1107
from adafruit_display_text import label


WHITE = 0xFFFFFF


def activate_oled_when_present() -> displayio.Display | None:
	try:
		WIDTH = 128
		HEIGHT = 64
		displayio.release_displays()
		i2c = board.I2C()
		display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
		display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
		return display
	except Exception:
		# No display found
		return None


def create_label(text: str, x: int, y: int) -> label.Label:
	return label.Label(terminalio.FONT, text=text, color=WHITE, x=x, y=y)


def ljust(text: str, min_length: int) -> str:
	my_string = text
	while len(my_string) < min_length:
		my_string = f" {my_string}"
	return my_string
		

class ControllerDisplay:
	
	def __init__(self) -> None:
		print("Initializing display...")
		display = activate_oled_when_present()
		if display is None:
			raise Exception("Could not find a display.")
		self.display: displayio.Display = display
		if self.display:
			self._build_display()
			print("Display initialized.")
		else:
			print("Could not find a display.")
	
	def _build_display(self) -> None:
		splash = displayio.Group()
		self.display.show(splash)
		self._state_label = create_label("STATE", 0, 9)
		splash.append(self._state_label)
		self._state_content = create_label("Waiting", 0, 21)
		splash.append(self._state_content)
		self._x_label = create_label("X", 75, 9)
		splash.append(self._x_label)
		self._y_label = create_label("Y", 115, 9)
		splash.append(self._y_label)
		self._x_content = create_label("  n/a", 50, 21)
		splash.append(self._x_content)
		self._y_content = create_label("  n/a", 90, 21)
		splash.append(self._y_content)

	def update_state(self, state: str) -> None:
		self._state_content.text = state

	def update_xy(self, x: int, y: int) -> None:
		x_val = ljust(str(x), 4)
		y_val = ljust(str(y), 4)
		self._x_content.text = f"{x_val}%"
		self._y_content.text = f"{y_val}%"
