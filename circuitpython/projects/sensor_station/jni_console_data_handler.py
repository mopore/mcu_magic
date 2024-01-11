from jni_motion_types import MotionEvent
from jni_data_handler import DataHandler
from jni_sensor_station import SensorData, SensorStation
import time


class ConsoleDataHandler(DataHandler):

	def __init__(self) -> None:
		self.present = False

	def handle(self, sensor_data: SensorData, now: float) -> None:
		motion_text = "-"
		if sensor_data.motion_event is not None:
			if sensor_data.motion_event.new_motion is MotionEvent.NEW_MOTION:
				motion_text = "New!"
				self.present = True
			else:
				motion_text = "Gone."
				self.present = False
		else:
			if self.present:
				motion_text = "(present)"
		print(f"Motion: {motion_text}")
		if sensor_data.light_level is not None:
			print(f"Light level: {sensor_data.light_level:.1f} Lumen")
		if sensor_data.aq is not None:
			print("CO2: %d ppm" % sensor_data.aq.co2)
			print("Temperature: %0.1f *C" % sensor_data.aq.temperature)
			print("Humidity: %0.1f %%" % sensor_data.aq.humidity)
		print()


def main() -> None:
	station = SensorStation()
	console_handler = ConsoleDataHandler()

	FREQUENCE_SECS = 1
	while True:
		last_time = time.monotonic()
		sensor_data = station.collect_data(True)
		console_handler.handle(sensor_data, last_time)	
		time_diff = time.monotonic() - last_time
		time_to_sleep = FREQUENCE_SECS - time_diff
		if time_to_sleep < 0:
			time_to_sleep = 0
			print("Did not have any time to sleep!")
		# print(f"Time difference to sleep: {time_to_sleep:.1f} secs")
		print()
		time.sleep(time_to_sleep)


if __name__ == "__main__":
	main()
