import time

import board
import pwmio

from adafruit_motor import servo


class FrontEngine:

	def __init__(self, pin_id, reverse: bool) -> None:
		pwm = pwmio.PWMOut(pin_id, frequency=50)
		self.c_servo = servo.ContinuousServo(pwm, min_pulse=750, max_pulse=2250)
		self.reverse = reverse

	def control(self, input: float) -> None:
		if self.reverse:
			input = -input
		self.c_servo.throttle = input


class SteeringEngine:
	
	def __init__(self, pin_id) -> None:
		pwm = pwmio.PWMOut(pin_id, frequency=50)
		# MG 995R servo can go from 0 to 180 degrees.
		self.s_servo = servo.Servo(pwm, min_pulse=600, max_pulse=2400)
		# Uncalibrated values: Center 90, Left 45 and Right 135
		self.max_left = 49
		self.max_right = 139
	
	def control(self, input: float) -> None:
		# Map input from -1 to 1 to max_left to max_right.
		angle = int((input + 1) / 2 * (self.max_right - self.max_left) + self.max_left)
		# print(f"Input: {input}, Angle: {angle}")
		self.s_servo.angle = angle


class EngineCalibration:
	
	def __init__(self) -> None:
		self.front_left = FrontEngine(board.IO14, reverse=False)  # type: ignore
		self.front_right = FrontEngine(board.IO12, reverse=True)  # type: ignore
		self.steering = SteeringEngine(board.IO6)  # type: ignore


def main() -> None:
	sleep_time = 2
	test_left_front = False
	test_right_front = False
	test_steering = True

	calibration = EngineCalibration()

	if test_left_front:
		print("Testing front left engine...")
		calibration.front_left.control(1)
		time.sleep(sleep_time)
		calibration.front_left.control(0)
		time.sleep(sleep_time)
		calibration.front_left.control(-1)
		time.sleep(sleep_time)
		calibration.front_left.control(0)
		time.sleep(sleep_time)

	if test_right_front:
		print("Testing front right engine...")
		calibration.front_right.control(1)
		time.sleep(sleep_time)
		calibration.front_right.control(0)
		time.sleep(sleep_time)
		calibration.front_right.control(-1)
		time.sleep(sleep_time)
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
