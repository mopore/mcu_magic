import time

import board
import pwmio

from adafruit_motor import servo


class FrontEngine:

	def __init__(self, pin_id, min_pulse: int, max_pulse: int, reverse: bool) -> None:
		pwm = pwmio.PWMOut(pin_id, frequency=50)
		self._c_servo = servo.ContinuousServo(pwm, min_pulse=min_pulse, max_pulse=max_pulse)
		self._reverse = reverse

	def control(self, input: float) -> None:
		if self._reverse:
			input = -input
		self._c_servo.throttle = input


class SteeringEngine:
	
	def __init__(self, pin_id, reverse: bool) -> None:
		pwm = pwmio.PWMOut(pin_id, frequency=50)
		# MG 995R servo can go from 0 to 180 degrees.
		self._s_servo = servo.Servo(pwm, min_pulse=600, max_pulse=2400)
		# Uncalibrated values: Center 90, Left 45 and Right 135
		self._max_left = 49
		self._max_right = 139
		self._reverse = reverse
	
	def control(self, input: float) -> None:
		if self._reverse:
			input = -input
		# Map input from -1 to 1 to max_left to max_right.
		angle = int((input + 1) / 2 * (self._max_right - self._max_left) + self._max_left)
		# print(f"Input: {input}, Angle: {angle}")
		self._s_servo.angle = angle


class EngineCalibration:
	
	def __init__(self) -> None:
		self.front_left = FrontEngine(
			board.IO14,  # type: ignore
			min_pulse=750,
			max_pulse=2250,
			reverse=False)
		self.front_right = FrontEngine(
			board.IO12,  # type: ignore
			min_pulse=760,
			max_pulse=2260,
			reverse=True)
		self.steering = SteeringEngine(board.IO6, reverse=True)  # type: ignore


def main() -> None:
	sleep_time = 2
	test_front_left = True
	test_front_right = True
	test_steering = False

	calibration = EngineCalibration()

	if test_front_left:
		print("Testing front left engine...")
		calibration.front_left.control(1)
		time.sleep(sleep_time)
		calibration.front_left.control(0)
		time.sleep(sleep_time)
		calibration.front_left.control(-1)
		time.sleep(sleep_time)
		calibration.front_left.control(0)
		time.sleep(sleep_time)

	if test_front_right:
		print("Testing front right engine...")
		calibration.front_right.control(1)
		time.sleep(sleep_time)
		calibration.front_right.control(0)
		time.sleep(sleep_time)
		calibration.front_right.control(-1)
		time.sleep(sleep_time)
		calibration.front_right.control(0)
		time.sleep(sleep_time)
		while True:
			calibration.front_right.control(0)
			time.sleep(sleep_time)

	if test_steering:
		print("Testing steering engine...")
		calibration.steering.control(0)
		# # Iterate from -1 to 1 in steps of 0.01.
		# for i in range(-100, 101, 1):
		# 	input = i / 100
		# 	calibration.steering.control(input)
		# 	time.sleep(0.1)
		time.sleep(1)


if __name__ == "__main__":
	main()
