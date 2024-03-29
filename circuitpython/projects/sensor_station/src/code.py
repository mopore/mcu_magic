# circup install adafruit_scd4x
# circup install adafruit_vl53l1x
# circup install adafruit_bh1750
# circup install adafruit_minimqtt
# circup install adafruit_datetime
# circup install adafruit_st7789

import time
import neopixel
import board
from jni_mqtt_data_handler import prepare_datahandler
from jni_sensor_station import SensorStation
from jni_data_handler import DataHandler
# from jni_tft_data_handler import TftDataHandler


def main() -> None:
	LED_RED = (255, 0, 0)
	LED_ORANGE = (255, 165, 0)

	np = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
	handlers: list[DataHandler] = []
	station_name = "teststation"
	try:
		station = SensorStation(np)
		features_airquality = station.provides_air_quality()

		if features_airquality:
			station_name = "broombed"
		else:
			station_name = "livingtv"
		print(f"Using the following name: {station_name}")

		# Use the console data viewer to output the collected data to the console...
		# handlers.append(ConsoleDataHandler())
		# handlers.append(TftDataHandler())
	except Exception as e:
		print(f"FATAL: Could not create essential services! {e}")
		for _ in range(5):
			np.fill(LED_ORANGE)
			time.sleep(0.3)
			np.fill(LED_RED)
			time.sleep(0.3)
		raise e

	mqtt_handler = prepare_datahandler(station_name, np)
	if mqtt_handler is not None:
		handlers.append(mqtt_handler)

	FREQUENCE_SECS = 0.25
	tickCounter = 0

	# We need a higher frequency for motion detection so I reduced the original
	# value from 0.5 to 0.25 seconds and introduced the fulltick variable.
	while True:
		last_timestamp = time.monotonic()

		tickCounter += 1
		fulltick = False
		if tickCounter == 3:
			fulltick = True
			tickCounter = 0
		sensor_data = station.collect_data(fulltick, last_timestamp)
		for handler in handlers:
			handler.handle(sensor_data, last_timestamp)

		time_diff = time.monotonic() - last_timestamp
		time_to_sleep = FREQUENCE_SECS - time_diff
		if time_to_sleep < 0:
			time_to_sleep = 0
			print("Did not have any time to sleep!")
		# print(f"Time difference to sleep: {time_to_sleep:.1f} secs")
		time.sleep(time_to_sleep)
		fulltick = not fulltick


if __name__ == "__main__":
	main()
