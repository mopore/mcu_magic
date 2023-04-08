import time

import board
import pwmio

from adafruit_motor import servo


def control(engines: list[servo.ContinuousServo], trottle_input: float) -> None:
	for engine in engines:
		engine.throttle = trottle_input


def main() -> None:
	pwms: list[pwmio.PWMOut] = [
		#  pwmio.PWMOut(board.IO14, frequency=50),  # type: ignore
		#  pwmio.PWMOut(board.IO12, frequency=50),  # type: ignore
		#  pwmio.PWMOut(board.IO6, frequency=50),  # type: ignore
		pwmio.PWMOut(board.IO5, frequency=50),  # type: ignore
	]

	engines: list[servo.ContinuousServo] = []
	for pwm in pwms:
		engine = servo.ContinuousServo(pwm, min_pulse=750, max_pulse=2250)
		engines.append(engine)

	print("Testing...")
	print("forward")
	control(engines, 1.0)
	time.sleep(2.0)
	print("stop")
	control(engines, -0.01)
	time.sleep(4.0)
	print("reverse")
	control(engines, -1.0)
	time.sleep(2.0)
	print("stop")
	control(engines, -0.01)
	time.sleep(4.0)


if __name__ == "__main__":
	main()
