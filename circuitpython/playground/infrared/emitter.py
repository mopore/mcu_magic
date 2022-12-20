
import board
import pulseio
import array
# import time


TV_ON_SIGNAL = [4527, 4479, 570, 1668, 576, 1662, 579, 1659, 573, 573, 549, 570, 552, 567, 552, 570, 552, 567, 543, 1668, 576, 1662, 579, 1659, 573, 573, 549, 570, 552, 567, 552, 567, 546, 573, 546, 576, 546, 1665, 579, 567, 552, 567, 546, 573, 546, 573, 549, 570, 552, 567, 555, 1656, 576, 570, 549, 1665, 579, 1659, 573, 1665, 576, 1662, 570, 1668, 576, 1662, 579]


class Emitter():

	def __init__(
		self,
	) -> None:
		# Preparing IR receiver
		# 50% duty cycle at 38kHz.
		self.pulse_out = pulseio.PulseOut(board.IO6, frequency=38000, duty_cycle=32768)
		self.pulses = array.array('H', TV_ON_SIGNAL)

	def emit(self) -> None:
		self.pulse_out.send(self.pulses)


def main() -> None:
	emitter = Emitter()
	print("Emitting...")
	emitter.emit()

	# while True:
	# 	print("Emitting...")
	# 	emitter.emit()
	# 	time.sleep(3)


if __name__ == "__main__":
	main()
