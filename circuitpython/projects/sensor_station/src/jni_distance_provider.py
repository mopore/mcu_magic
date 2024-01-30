# circup install adafruit_vl53l1x

import time
import board
import neopixel
import adafruit_vl53l1x

from jni_motion_types import MotionEventProvider, MotionEvent


class MotionDetector:

	INIT_VALUE = -1
	TOLERANCE_CM = 15

	def __init__(self, baseline: float, vl53) -> None:
		self.baseline = baseline
		self.new_motion_detected = False
		self.proofText: str | None = None
		self.vl53 = vl53

	def read(self, first: float | None) -> None | float:
		if self._value_fails(first):
			return None

		second = self._readNext()
		if self._value_fails(second):
			return None

		third = self._readNext()
		if self._value_fails(third):
			return None

		self.proofText = f"base {self.baseline}cm,  1: {first}cm,  2: {second}cm,  3: {third}cm"
		self.new_motion_detected = True
		return first

	def collect_motion_detected(self) -> str | None:
		if self.new_motion_detected:
			self.new_motion_detected = False
			return self.proofText
		return None

	def _value_fails(self, reading: float | None) -> bool:
		if reading is None:
			return True

		if reading > self.baseline:
			return True

		diff_candidate1 = abs(reading - self.baseline)
		if diff_candidate1 < self.TOLERANCE_CM:
			return True

		return False

	def _readNext(self) -> float | None:
		time.sleep(0.1)
		failCounter = 0
		while failCounter < 3:
			if self.vl53.data_ready:
				current = self.vl53.distance
				self.vl53.clear_interrupt()
				if current is None:
					failCounter += 1
				else:
					return current


class DistanceMotionEventProvider(MotionEventProvider):

	NO_PROOF_TEXT = "<no proof provided>"
	NEW_MOTION_TIME_THRESHOLD = 6
	TRIGGER_DISTANCE_CM = 150
	MODE_LONG = 2

	NO_MOVE_THRESHOLD_CM = 3
	STABLE_FOR_CALIBRATION_SEC = 10

	NP_GREEN = (0, 255, 0)
	NP_PURPLE = (255, 0, 255)
	NP_YELLOW = (255, 255, 0)
	NP_RED = (255, 0, 0)
	NP_BLACK = (0, 0, 0)

	def __init__(self, np: neopixel.NEOPIXEL | None) -> None:
		self.in_motion = False
		self.last_motion_trigger = 0

		if np is None:
			self.onboard_np = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
			self.onboard_np.brightness = 0.03
		else:
			self.onboard_np = np
		self.onboard_np.fill(self.NP_PURPLE)

		print("Initializing VL53L1X sensor...")
		# For Adafruit Qt Py ESP32-S3 we need the STEMMA_I2C
		# Default would be I2C
		#
		# i2c = board.I2C()
		i2c = board.STEMMA_I2C()  # type: ignore
		vl53 = adafruit_vl53l1x.VL53L1X(i2c)
		vl53.distance_mode = self.MODE_LONG
		# vl53.timing_budget = 200
		vl53.timing_budget = 100
		vl53.start_ranging()
		self.vl53 = vl53
		first_reading = self._first_reading()
		self.baseline = self._calibrate(first_reading)
		self.detector = MotionDetector(self.baseline, vl53)

	def _first_reading(self) -> float:
		print("Testing distance sensor...")
		first_reading: float | None = None
		while first_reading is None:
			if self.vl53.data_ready:
				first_reading = self.vl53.distance
				self.vl53.clear_interrupt()
		print("Distance sensor is functional!")
		return first_reading

	def _calibrate(self, first_reading: float) -> float:
		print("Determining baseline distance...")
		baseline = first_reading
		last_distance_time = time.monotonic()
		fist_distance_time = last_distance_time
		while True:
			now = time.monotonic()
			time_passed = now - last_distance_time
			time_passed_first = now - fist_distance_time
			if self.vl53.data_ready:
				current = self.vl53.distance
				diff = abs(current - baseline)
				if diff < self.NO_MOVE_THRESHOLD_CM:
					self.onboard_np.fill(self.NP_YELLOW)
					if time_passed > self.STABLE_FOR_CALIBRATION_SEC:
						self.onboard_np.fill(self.NP_BLACK)
						self.onboard_np.brightness = 0
						if current is None:
							raise Exception("Could not calibrate distance sensor!")
						print(f"Threshold calibrated to {current}")
						return current
				else:
					self.onboard_np.fill(self.NP_RED)
					baseline = current
					last_distance_time = now
			time.sleep(0.5)
			if time_passed_first > 3 * self.STABLE_FOR_CALIBRATION_SEC:
				raise Exception("Could not calibrate distance sensor in time!")

	# The caller of this function expects three possible return scenarios:
	# - None: No motion event
	# - MotionEvent(MotionEvent.MOTION_GONE)
	# - MotionEvent(MotionEvent.NEW_MOTION)
	#
	# The function is intended to be called in a loop every 0.24 seconds.
	def get_motion_event(self):
		motion_event: MotionEvent | None = None
		proof = self.NO_PROOF_TEXT
		now_reading: None | float = None
		if self.vl53.data_ready:
			now_reading = self.detector.read(self.vl53.distance)
			self.vl53.clear_interrupt()

			movement_now = False

			if now_reading is not None and now_reading < self.TRIGGER_DISTANCE_CM:
				detection_result = self.detector.collect_motion_detected()
				if detection_result is not None:
					movement_now = True
					proof = detection_result
					motion_event = self._when_movement_now()

			if self.in_motion and not movement_now:
				current_timestamp = time.time()
				time_after_trigger = current_timestamp - self.last_motion_trigger
				if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
					self.in_motion = False
					motion_event = MotionEvent(MotionEvent.MOTION_GONE)

		if motion_event is None:
			return None
		else:
			print(f"Motion (new: {motion_event.new_motion}) w/ proof: {proof}")
			return motion_event, proof

	def _when_movement_now(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		self.last_motion_trigger = time.time()
		if self.in_motion is False:
			self.in_motion = True
			motion_event = MotionEvent(MotionEvent.NEW_MOTION)
		return motion_event


def main() -> None:
	np = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
	provider = DistanceMotionEventProvider(np)
	while True:
		result = provider.get_motion_event()
		if result is not None:
			print(f"Distance: {result} cm")
		else:
			print("No read...")
		time.sleep(0.5)


if __name__ == "__main__":
	main()
