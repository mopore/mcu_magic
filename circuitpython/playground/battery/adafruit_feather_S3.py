# See: https://github.com/adafruit/Adafruit_CircuitPython_LC709203F
# Ensure to have "adafruit_lc709203f" installed (circup install adafruit_lc709203f)
import time
import board
from adafruit_lc709203f import LC709203F, PackSize

BATTERY_MON_ADDRESS = 0x0B  # Address for ESP32-s3 tft Feather


def hack_for_i2c_issue():
	i2c = board.I2C()
	while not i2c.try_lock():
		pass
	running = True
	try:
		while running:
			print("I2C addresses found:", 
				[hex(device_address) for device_address in i2c.scan()]
			)
			# time.sleep(2)
			running = False
		return i2c
	finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
		i2c.unlock()


def main() -> None:

	try:
		print("Searching for battery monitor...")

		# There is a known issue with the ESP32-S3: 
		# https://github.com/adafruit/circuitpython/issues/6311
		# Therefore this will not work -> board.I2C()
		i2c = hack_for_i2c_issue()
		battery_monitor = LC709203F(i2c)

		# Update to match the mAh of your battery for more accurate readings.
		# Can be MAH100, MAH200, MAH400, MAH500, MAH1000, MAH2000, MAH3000.
		# Choose the closest match. Include "PackSize." before it, as shown.
		battery_monitor.pack_size = PackSize.MAH100  # type: ignore

		while True:
			print(f"Battery Percent: {battery_monitor.cell_percent:.2f} %")
			print(f"Battery Voltage: {battery_monitor.cell_voltage:.2f} V")
			time.sleep(2)

	except Exception as e:
		print(f"Error reading battery: {e}")
	print("All done.")


if __name__ == "__main__":
	main()
