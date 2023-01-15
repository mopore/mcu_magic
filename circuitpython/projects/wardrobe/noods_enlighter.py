import board
import time
import pwmio


class NoodsEnlighter:
	
	DUTY_CYCLES = [
		0,
		29,
		307,
		1612,
		3852,
		6752,
		10071,
		13463,
		16574,
		19146,
		20865,
		21598
	]

	def __init__(self, pin) -> None:
		self.pwm_out = pwmio.PWMOut(pin, frequency=1000, duty_cycle=0)

	def light_up(self) -> None:
		for i in range(len(self.DUTY_CYCLES)):
			brightness = self.DUTY_CYCLES[i]
			self.pwm_out.duty_cycle = brightness
			time.sleep(.08)

	def light_down(self) -> None:
		for i in reversed(range(len(self.DUTY_CYCLES))):
			brightness = self.DUTY_CYCLES[i]
			self.pwm_out.duty_cycle = brightness
			time.sleep(.08)	


def main() -> None:
	print("Starting up...")

	# UM Feather S3
	# pin = digitalio.DigitalInOut(board.IO5)  # type: ignore
	
	# Adafruit QT Py ESP32-S3
	pin = board.MOSI
	
	enlighter = NoodsEnlighter(pin)

	for _ in range(3):
		enlighter.light_up()
		time.sleep(2)
		enlighter.light_down()
		time.sleep(2)


if __name__ == "__main__":
	main()
