import time
import board

import distance_provider
import noods_enlighter
import neopixel


NOODS_ON = True
NOODS_OFF = False


class ThresholdProvider:

	STATE_AWAITING_STABLE_VALUE = 0
	STATE_CALIBRATED = 1

	NO_MOVE_THRESHOLD_CM = 3
	STABLE_FOR_CALIBRATION_SEC = 10

	NP_GREEN = (0, 255, 0)
	NP_RED = (255, 0, 0)
	NP_BLACK = (0, 0, 0)

	def __init__(self) -> None:
		self.state = self.STATE_AWAITING_STABLE_VALUE
		self.last_distance = -1
		self.last_distance_time = 0
		self.distance_threshold = -1
		self.onboard_np = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
		self.onboard_np.brightness = 0.03
		self.onboard_np.fill(self.NP_GREEN)

	def calibrate(self, distance: float) -> None:
		now = time.monotonic()
		if self.last_distance < 0:
			self.last_distance = distance
			self.last_distance_time = now
			print("Waiting for stable value for door threshold...")
		else:
			if self.STATE_AWAITING_STABLE_VALUE == self.state:
				diff = abs(self.last_distance - distance)
				
				if diff < self.NO_MOVE_THRESHOLD_CM:
					self.onboard_np.fill(self.NP_GREEN)
					time_passed = now - self.last_distance_time
					if time_passed > self.STABLE_FOR_CALIBRATION_SEC:
						self.distance_threshold = distance
						self.onboard_np.fill(self.NP_BLACK)
						self.onboard_np.brightness = 0
						self.last_noods_off = time.monotonic()
						self.state = self.STATE_CALIBRATED
						print(f"Threshold calibrated to {distance}")
				else:
					self.onboard_np.fill(self.NP_RED)
					self.last_distance = distance
					self.last_distance_time = now

	def get_desired_state(self, distance: float) -> bool:
		if distance - self.NO_MOVE_THRESHOLD_CM > self.distance_threshold:
			return NOODS_ON
		else:
			return NOODS_OFF


def main() -> None:
	print("Starting...")
	dp = distance_provider.DistanceProvider()
	pin = board.MOSI  # Adafruit QT Py ESP32-S3
	enligher = noods_enlighter.NoodsEnlighter(pin)
	current_noods_state = NOODS_OFF
	thresholdProvider = ThresholdProvider()
	last_turn_off_request: float = 0

	while True:
		distance = dp.read_distance()
		if distance is not None:
			needs_calibration = ThresholdProvider.STATE_CALIBRATED != thresholdProvider.state
			if needs_calibration:
				thresholdProvider.calibrate(distance)
			else:
				desired_noods_state = thresholdProvider.get_desired_state(distance)
				if desired_noods_state != current_noods_state:
					if desired_noods_state == NOODS_ON:
						last_turn_off_request = 0
						current_noods_state = desired_noods_state
						enligher.light_up()
					else:
						if last_turn_off_request == 0:
							last_turn_off_request = time.monotonic()
						else:
							time_passed = time.monotonic() - last_turn_off_request
							if time_passed > 0:
								current_noods_state = desired_noods_state
								enligher.light_down()
						
		time.sleep(.2)


if __name__ == "__main__":
	main()
