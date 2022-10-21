# See: https://github.com/adafruit/Adafruit_CircuitPython_LC709203F
# Ensure to have "adafruit_lc709203f" installed (circup install adafruit_lc709203f)
import time
import board
from adafruit_lc709203f import LC709203F, PackSize

# There is a known issue with the ESP32-S3: 
# https://github.com/adafruit/circuitpython/issues/6311

try:
	address = 0x0B  # Address for ESP32-s3 tft Feather
	# Create sensor object, using the board's default I2C bus.
	print("Searching for battery monitor...")
	battery_monitor = LC709203F(board.I2C(), address=address)

	# Update to match the mAh of your battery for more accurate readings.
	# Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
	# Choose the closest match. Include "PackSize." before it, as shown.
	battery_monitor.pack_size = PackSize.MAH100  # type: ignore

	while True:
		print("Battery Percent: {:.2f} %".format(battery_monitor.cell_percent))
		print("Battery Voltage: {:.2f} V".format(battery_monitor.cell_voltage))
		time.sleep(2)

except Exception as e:
	print(f"Error reading battery: {e}")
	print("All done.")
