# circup install adafruit_scd4x
# circup install adafruit_vl53l1x
# circup install adafruit_bh1750
# circup install adafruit_minimqtt
# circup install adafruit_datetime
# circup install adafruit_st7789

import time
from jni_mqtt_data_handler import prepare_datahandler
from jni_sensor_station import SensorStation
from jni_data_handler import DataHandler
from jni_console_data_handler import ConsoleDataHandler
# from jni_tft_data_handler import TftDataHandler


def main() -> None:
	station = SensorStation()

	# Use the console data viewer to output the collected data to the console...
	handlers: list[DataHandler] = [
		ConsoleDataHandler(), 
		# TftDataHandler(),
	]
	mqtt_handler = prepare_datahandler()
	if mqtt_handler is not None:
		handlers.append(mqtt_handler)

	FREQUENCE_SECS = 0.5
	while True:
		last_time = time.monotonic()
		sensor_data = station.collect_data()
		for handler in handlers:
			handler.handle(sensor_data)

		time_diff = time.monotonic() - last_time
		time_to_sleep = FREQUENCE_SECS - time_diff
		if time_to_sleep < 0:
			time_to_sleep = 0
			print("Did not have any time to sleep!")
		# print(f"Time difference to sleep: {time_to_sleep:.1f} secs")
		time.sleep(time_to_sleep)


if __name__ == "__main__":
	main()
