# circup install adafruit_irremote
import board
import pulseio
import adafruit_irremote

BUTTON_YES = False
BUTTON_NO = True

TV_ON_PULSE = [4530, 4476, 573, 1665, 579, 1659, 573, 1665, 579, 564, 546, 573, 549, 573, 549, 570, 549, 570, 543, 1692, 549, 1689, 543, 1668, 576, 570, 552, 567, 552, 567, 546, 573, 546, 573, 549, 570, 552, 1686, 546, 573, 549, 573, 549, 570, 549, 570, 543, 576, 546, 573, 546, 1692, 552, 567, 543, 1695, 549, 1662, 579, 1659, 573, 1665, 579, 1659, 573, 1665, 579]


class InfraredRecoder():

	def __init__(
		self,
	) -> None:
		self.decoder = adafruit_irremote.GenericDecode()
		
		# Preparing IR receiver
		self.pulses = pulseio.PulseIn(board.IO6, maxlen=200, idle_state=True)  # type: ignore  

	def tick(self) -> None:
		self.record()
	
	def fuzzy_pulse_compare(self, recording, fuzzyness=0.2) -> bool:
		if len(recording) != len(TV_ON_PULSE):
			return False
		for i in range(len(recording)):
			threshold = int(recording[i] * fuzzyness)
			if abs(recording[i] - TV_ON_PULSE[i]) > threshold:
				return False
		return True

	def record(self) -> None:
		print("Waiting for infrared signal to compare...")
		self.pulses.clear()
		self.pulses.resume()
		pulse = self.decoder.read_pulses(self.pulses)
		self.pulses.pause()
		if pulse is not None:
			comparison = self.fuzzy_pulse_compare(pulse)
			print(f"Comparison with TV ON pulse: {comparison}")
		else:
			print("Could not read anything.")


def main() -> None:
	recorder = InfraredRecoder()

	while True:
		recorder.tick()


if __name__ == "__main__":
	main()
