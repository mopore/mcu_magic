# circup install adafruit_vl53l1x

import time
import board
import adafruit_vl53l1x

from jni_motion_types import MotionEventProvider, MotionEvent


class MotionDetector:

	INIT_VALUE = -1
	TOLERANCE_CM = 15

	def __init__(self) -> None:
		self.baseline: None | int = None
		self.candidate1: None | int = None
		self.candidate2: None | int = None
		self.new_motion_detected = False

	def read(self, raw: float | None) -> None | int:
		if raw is None:
			return
		current = int(raw)

		if self.baseline is None:
			self.baseline = current
		else:
			if self.candidate1 is None:
				diff_baseline1 = abs(current - self.baseline)
				new_candidate1 = diff_baseline1 > self.TOLERANCE_CM
				if new_candidate1:
					self.candidate1 = current
			elif self.candidate2 is None:
				diff_baseline2 = abs(current - self.baseline)
				new_candidate2 = diff_baseline2 > self.TOLERANCE_CM
				if new_candidate2:
					self.candidate2 = current
				else:
					self.candidate1 = None
			else:  # candidate1 and candidate2 are set
				diff_confirmation = abs(current - self.baseline)
				candidate_confirmed = diff_confirmation > self.TOLERANCE_CM
				if candidate_confirmed:
					self.baseline = current
					self.new_motion_detected = True
				self.candidate1 = None
				self.candidate2 = None
		return current

	def is_motion_detected(self) -> bool:
		if self.new_motion_detected:
			self.new_motion_detected = False
			return True
		return False


class DistanceMotionEventProvider(MotionEventProvider):

	NEW_MOTION_TIME_THRESHOLD = 6
	TRIGGER_DISTANCE_CM = 150
	MODE_LONG = 2

	def __init__(self) -> None:
		self.last_motion_trigger = 0
		self.detector = MotionDetector()

		print("Initializing VL53L1X sensor...")
		# For Adafruit Qt Py ESP32-S3 we need the STEMMA_I2C
		# Default would be I2C
		#
		# i2c = board.I2C()
		i2c = board.STEMMA_I2C()  # type: ignore
		vl53 = adafruit_vl53l1x.VL53L1X(i2c)
		vl53.distance_mode = self.MODE_LONG
		vl53.timing_budget = 200
		vl53.start_ranging()
		self.vl53 = vl53

		print("Testing distance sensor...")
		first_reading = False
		while not first_reading:
			if self.vl53.data_ready:
				self.younger_reading = self.vl53.distance
				first_reading = True
				self.vl53.clear_interrupt()

		self.in_motion = False
		print("Distance sensor is set up.")

	# The caller of this function expects three possible return scenarios:
	# - None: No motion event
	# - MotionEvent(MotionEvent.MOTION_GONE)
	# - MotionEvent(MotionEvent.NEW_MOTION)
	#
	# The function is intended to be called in a loop every 0.24 seconds.
	def get_motion_event(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		now_reading: None | float = None
		if self.vl53.data_ready:
			now_reading = self.detector.read(self.vl53.distance)
			self.vl53.clear_interrupt()

			movement_now = False

			if now_reading is not None and now_reading < self.TRIGGER_DISTANCE_CM:
				if self.detector.is_motion_detected():
					movement_now = True
					motion_event = self._when_movement_now()

			if self.in_motion and not movement_now:
				current_timestamp = time.time()
				time_after_trigger = current_timestamp - self.last_motion_trigger
				if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
					self.in_motion = False
					print("Motion is gone. Will trigger callback...")
					motion_event = MotionEvent(MotionEvent.MOTION_GONE)

			self.older_reading = self.younger_reading
			self.younger_reading = now_reading
		return motion_event

	def _when_movement_now(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		self.last_motion_trigger = time.time()
		if self.in_motion is False:
			self.in_motion = True
			print("New Motion detected.")
			motion_event = MotionEvent(MotionEvent.NEW_MOTION)
		return motion_event


def main() -> None:
	provider = DistanceMotionEventProvider()
	while True:
		result = provider.get_motion_event()
		if result is not None:
			print(f"Distance: {result} cm")
		else:
			print("No read...")
		time.sleep(0.5)


if __name__ == "__main__":
	main()
