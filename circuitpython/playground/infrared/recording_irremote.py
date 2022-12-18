# circup install adafruit_irremote
import board
import pulseio
import adafruit_irremote

BUTTON_YES = False
BUTTON_NO = True


class InfraredRecoder():

	def __init__(
		self,
	) -> None:
		self.decoder = adafruit_irremote.GenericDecode()
		
		# Preparing IR receiver
		self.pulses = pulseio.PulseIn(board.IO6, maxlen=200, idle_state=True)  # type: ignore  

	def tick(self) -> None:
		self.record()

	def record(self) -> None:
		print("Waiting for infrared signal...")
		self.pulses.clear()
		self.pulses.resume()
		pulse = self.decoder.read_pulses(self.pulses)
		self.pulses.pause()
		if pulse is not None:
			print(f"Length of pulses: {len(pulse)}")
			print(f"Recording: {pulse}")
		else:
			print("Could not read anything.")


def main() -> None:
	recorder = InfraredRecoder()

	while True:
		recorder.tick()


if __name__ == "__main__":
	main()
