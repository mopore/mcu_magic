import displayio
import struct
import time
import board
import random

import adafruit_displayio_sh1107
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement


def create_payload() -> bytes:
	x = random.randint(-100, 100)
	y = random.randint(-100, 100)
	payload = struct.pack("<bb", x, y)
	return payload


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
		print("Could not find a display.")
		return None


activate_oled_when_present()
print("Starting BLE in 5 seconds...")
time.sleep(5)

ble = BLERadio()
advertisement = Advertisement()
print("Starting advertising...")
advertisement.complete_name = "jnitest"
advertisement.connectable = True

ble.start_advertising(advertisement, interval=0.1)
print(advertisement)

while True:
	while not ble.connected:
		pass
	print("connected")
	while ble.connected:
		pass
	print("disconnected")
