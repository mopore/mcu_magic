import time
import board

import adafruit_vl53l1x


class DistanceProvider:

	def __init__(self) -> None:
		# Prepare VL53L1X
		MODE_LONG = 2
		i2c = board.STEMMA_I2C()  # type: ignore
		vl53 = adafruit_vl53l1x.VL53L1X(i2c)
		vl53.distance_mode = MODE_LONG
		vl53.start_ranging()
		self.sensor = vl53

	def read_distance(self) -> float | None:
		if self.sensor.data_ready:
			distance = self.sensor.distance
			if distance is not None:
				try:
					return distance
				except Exception as e:
					print(e)
			self.sensor.clear_interrupt()


def main() -> None:
	dp = DistanceProvider()

	while True:                            # Repeat forever...
		distance = dp.read_distance()
		if distance is not None:
			print(f"Distance: {distance:.0f} cm", end="\r")
		time.sleep(.2)


if __name__ == "__main__":
	main()
