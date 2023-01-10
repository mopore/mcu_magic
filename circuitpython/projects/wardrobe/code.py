import time
import math

import board
import pwmio

import adafruit_vl53l1x


def main() -> None:

	# Prepare VL53L1X
	MODE_LONG = 2
	i2c = board.I2C()
	vl53 = adafruit_vl53l1x.VL53L1X(i2c)
	vl53.distance_mode = MODE_LONG
	vl53.start_ranging()

	# Prepare LED
	PINS = [board.A2]  # type: ignore List of pins, one per nOOd
	GAMMA = 2.6  # For perceptually-linear brightness
	pin_list = [pwmio.PWMOut(pin, frequency=1000, duty_cycle=0) for pin in PINS]

	while True:                            # Repeat forever...
		for i, pin in enumerate(pin_list):  # For each pin...
			phase = (time.monotonic() - 2 * i / len(PINS)) * math.pi
			brightness = int((math.sin(phase) + 1.0) * 0.5 ** GAMMA * 65535 + 0.5)
			pin.duty_cycle = brightness
			if vl53.data_ready:
				try:
					print(f"Distance: {vl53.distance:.0f} cm", end="\r")
				except Exception as e:
					print(e)
				vl53.clear_interrupt()
				time.sleep(.1)


if __name__ == "__main__":
	main()
