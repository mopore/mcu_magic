# circup install adafruit_vl53l1x

import time
import board
from digitalio import DigitalInOut, Pull

from jni_motion_types import MotionEventProvider, MotionEvent


class PirMotionEventProvider(MotionEventProvider):

	MOTION_YES = True
	MOTION_NO = False
	NEW_MOTION_TIME_THRESHOLD = 6
	#  BOARD_PIN = board.D13  # Adafruit TFT Feather name
	BOARD_PIN = board.A0  # Adafruit QT Py ESP32-S3

	def __init__(self) -> None:
		self.last_new_motion_timestamp = 0
		self.last_motion_trigger = 0
		self.current_motion = self.MOTION_NO
		motion_pin = DigitalInOut(self.BOARD_PIN)  # Adafruit TFT Feather name
		motion_pin.switch_to_input(pull=Pull.UP)
		self.motion_pin = motion_pin
		self.okay = True

	def get_motion_event(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		pin_value = self.motion_pin.value
		if pin_value is self.MOTION_YES:
			motion_event = self._when_motion()
		if self.current_motion:
			current_timestamp = time.time()
			time_after_trigger = current_timestamp - self.last_motion_trigger
			if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
				self.current_motion = self.MOTION_NO
				motion_event = MotionEvent(MotionEvent.MOTION_GONE)
		return motion_event

	def _when_motion(self) -> MotionEvent | None:
		motion_event: MotionEvent | None = None
		current_timestamp = time.time()
		self.last_motion_trigger = current_timestamp
		time_after_last_new_motion = current_timestamp - self.last_new_motion_timestamp
		if time_after_last_new_motion > self.NEW_MOTION_TIME_THRESHOLD:
			self.last_new_motion_timestamp = current_timestamp
			if self.current_motion is self.MOTION_NO:
				self.current_motion = True
				motion_event = MotionEvent(MotionEvent.NEW_MOTION)
		return motion_event
		

def main() -> None:
	provider = PirMotionEventProvider()
	while True:
		result = provider.get_motion_event()
		if result is not None:
			if result.new_motion is MotionEvent.NEW_MOTION:
				print("New Motion!")
			else:
				print("Motion is gone.")
		time.sleep(0.5)


if __name__ == "__main__":
	main()
