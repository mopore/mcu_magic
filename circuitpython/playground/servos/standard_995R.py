import time

import board
import pwmio

from adafruit_motor import servo


def control(engines: list[servo.Servo], angle: int) -> None:
	for engine in engines:
		engine.angle = angle


def main() -> None:
	pwms: list[pwmio.PWMOut] = [
		pwmio.PWMOut(board.IO6, frequency=50),  # type: ignore
	]

	engines: list[servo.Servo] = []
	for pwm in pwms:
		engine = servo.Servo(pwm, min_pulse=600, max_pulse=2400)
		engines.append(engine)

	angles = [90, 45, 0, 45, 90, 135, 180, 135, 90]
	# angles = [90, 45, 90, 135, 90]  # For testing as car steering.

	print("Testing...")
	
	for angle in angles:
		print(angle)
		control(engines, angle)
		time.sleep(2.0)


if __name__ == "__main__":
	main()
