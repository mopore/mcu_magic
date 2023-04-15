# circup install adafruit_pct2075
import time
import board
import adafruit_pct2075


class TemperatureProvider:

	def __init__(self) -> None:
		i2c = board.STEMMA_I2C()  # type: ignore # For Adafruit QTPy ESP32-S3
		self.pct = adafruit_pct2075.PCT2075(i2c)

	def read_temperature(self) -> float | None:
		return self.pct.temperature


def main() -> None:
	print("Starting...")
	provider = TemperatureProvider()
	while True:
		temp = provider.read_temperature()
		print(f"Temperature: {temp:.1f} °C", end="\r")
		time.sleep(2)


if __name__ == "__main__":
	main()
