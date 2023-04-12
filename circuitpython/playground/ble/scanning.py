from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
import time
print("Starting BLE in 5 seconds...")
time.sleep(5)

ble = BLERadio()
print("scanning...")
start_time = time.monotonic()
advertisements = ble.start_scan(ProvideServicesAdvertisement, Advertisement, timeout=5)

counter_not_us = 0

for advertisement in advertisements:
	try:
		name = advertisement.complete_name
		scan_response_present = advertisement.scan_response
		if scan_response_present:
			if advertisement.complete_name == "jnitest":
				print("Found jnitest!")
				print(advertisement.data_dict)
				connection = ble.connect(advertisement)
				print("connected")
				time.sleep(1)
				connection.disconnect()
	except Exception as err:
		print(f"Problem with advertisement: {err}")
print("scanning done")
time_passed = time.monotonic() - start_time
print(f"Time passed: {time_passed} seconds")
