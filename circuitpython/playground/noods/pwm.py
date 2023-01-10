import time
import math

import board
import pwmio


def main() -> None:

	# This uses the 3 adjacent SPI pins on QtPy RP2040, but any pins will do.
	PINS = [board.IO5]  # type: ignore List of pins, one per nOOd
	GAMMA = 2.6  # For perceptually-linear brightness

	# Convert pin number list to PWMOut object list
	pin_list = [pwmio.PWMOut(pin, frequency=1000, duty_cycle=0) for pin in PINS]

	while True:                            # Repeat forever...
		for i, pin in enumerate(pin_list):  # For each pin...
			# Calc sine wave, phase offset for each pin, with gamma correction.
			# If using red, green, blue nOOds, you'll get a cycle of hues.
			phase = (time.monotonic() - 2 * i / len(PINS)) * math.pi
			brightness = int((math.sin(phase) + 1.0) * 0.5 ** GAMMA * 65535 + 0.5)
			pin.duty_cycle = brightness


if __name__ == "__main__":
	main()
