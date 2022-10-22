# circup install adafruit_vl53l1x

# Time of Flight
# Documentation: https://learn.adafruit.com/adafruit-vl53l1x/overview

# Used the UM FeatherS3

# Connected just the I2C pins (VIN, SCL, SDA, GND) 2nd to 5th pin
# Note that SDA and SCL are twisted (compared to FeatherS3)


import time
import board
import adafruit_vl53l1x


class DistanceProvider:

	def __init__(self) -> None:
		MODE_LONG = 2

		# i2c = board.I2C()
		i2c = board.STEMMA_I2C()  # type: ignore

		vl53 = adafruit_vl53l1x.VL53L1X(i2c)

		# OPTIONAL: can set non-default values
		vl53.distance_mode = MODE_LONG
		vl53.timing_budget = 100
		vl53.start_ranging()
		self.sensor = vl53

	def get_distance(self) -> float | None:
		while not self.sensor.data_ready:
			pass
		result = self.sensor.distance
		self.sensor.clear_interrupt()
		return result


def main() -> None:

	provider = DistanceProvider()
	while True:
		result = provider.get_distance()
		if result is not None:
			print(f"Distance: {result} cm")
		else:
			print("No read...")
			time.sleep(1.0)


if __name__ == "__main__":
	main()
