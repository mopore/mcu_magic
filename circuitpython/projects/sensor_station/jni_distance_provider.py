# circup install adafruit_vl53l1x

import time
import board
import adafruit_vl53l1x

from jni_motion_types import MotionEventProvider, MotionEvent


class DistanceMotionEventProvider(MotionEventProvider):

	TRIGGER_DISTANCE_CM = 150
	NEW_MOTION_TIME_THRESHOLD = 6
	INIT_VALUE = -1

	def __init__(self) -> None:
		MODE_LONG = 2

		# i2c = board.I2C()
		i2c = board.STEMMA_I2C()  # type: ignore

		vl53 = adafruit_vl53l1x.VL53L1X(i2c)
		vl53.distance_mode = MODE_LONG
		vl53.timing_budget = 100
		vl53.start_ranging()
		self.sensor = vl53

		self.last_reading: None | float = self.INIT_VALUE
		self.last_new_motion_timestamp = 0
		self.current_motion = False

	def _read_distance(self) -> float | None:
		while not self.sensor.data_ready:
			pass
		result = self.sensor.distance
		self.sensor.clear_interrupt()
		return result

	def get_motion_event(self) -> MotionEvent | None:
		reading = self._read_distance()
		motion_event: MotionEvent | None = None
		if self.last_reading == self.INIT_VALUE:
			self.last_reading = reading
		movement_now = False
		if reading is not None and reading < self.TRIGGER_DISTANCE_CM:
			if self.last_reading is None:
				movement_now = True
				motion_event = self._when_movement_now()
			else:    
				# Check if not a static object is present
				diff = self.last_reading - reading
				if abs(diff) > 2: 
					movement_now = True
					motion_event = self._when_movement_now()
		if movement_now is False and self.current_motion is True:
			current_timestamp = time.time()
			time_after_trigger = current_timestamp - self.last_new_motion_timestamp
			if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
				self.current_motion = False
				motion_event = MotionEvent(MotionEvent.MOTION_GONE)
		self.last_reading = reading
		return motion_event
	
	def _when_movement_now(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		try:
			self.last_new_motion_timestamp = time.time()
			if self.current_motion is False:
				self.current_motion = True
				motion_event = MotionEvent(MotionEvent.NEW_MOTION)
		except Exception as e:
			error_message = f"Error with Motion Handler when handling motion: {e}"
			raise Exception(error_message)
		return motion_event
		

def main() -> None:
	provider = DistanceMotionEventProvider()
	while True:
		result = provider._read_distance()
		if result is not None:
			print(f"Distance: {result} cm")
		else:
			print("No read...")
		time.sleep(0.5)


if __name__ == "__main__":
	main()
