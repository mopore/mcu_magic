# circup install adafruit_irremote
import board
import pulseio
import time

TV_ON_SIGNAL = [4527, 4479, 570, 1668, 576, 1662, 579, 1659, 573, 573, 549, 570, 552, 567, 552, 570, 552, 567, 543, 1668, 576, 1662, 579, 1659, 573, 573, 549, 570, 552, 567, 552, 567, 546, 573, 546, 576, 546, 1665, 579, 567, 552, 567, 546, 573, 546, 573, 549, 570, 552, 567, 555, 1656, 576, 570, 549, 1665, 579, 1659, 573, 1665, 576, 1662, 570, 1668, 576, 1662, 579]


class InfraredRecoder():

	def __init__(
		self,
	) -> None:
		self.catch_counter = 0
		self.last_check_time = 0
		self.button_ready = True
		self.recording = False
		self.last_length = 0
		
		# Preparing IR receiver
		self.pulse_in = pulseio.PulseIn(board.IO6, maxlen=1000, idle_state=True)  # type: ignore  

		print("Listening to signals...")

	def record(self) -> None:
		length = len(self.pulse_in)
		if length > 0:
			if self.last_length == length:
				now = time.monotonic()
				time_passed = now - self.last_check_time
				if time_passed > 1:
					# More then 1 second the same length of pulses
					self._handle_yield(length)
					self.last_length = 0
			else:
				self.last_length = length
				self.last_check_time = time.monotonic()
	
	def _handle_yield(self, length: int) -> None:
		self.catch_counter += 1
		self.pulse_in.pause()
		print(f"Received pulses #{self.catch_counter} with a length of {length}:")
		pulses_list = [self.pulse_in[i] for i in range(length)]
		comparison_result = self.fuzzy_pulse_compare(pulses_list)	
		print(f"Comparison with Samsung TV On signal: {comparison_result}\n")
		self.pulse_in.clear()
		self.pulse_in.resume()
	
	def fuzzy_pulse_compare(self, recording: list[int], fuzzyness=0.2) -> bool:
		if len(recording) < len(TV_ON_SIGNAL):
			return False
		for i in range(len(TV_ON_SIGNAL)):
			threshold = int(recording[i] * fuzzyness)
			if abs(recording[i] - TV_ON_SIGNAL[i]) > threshold:
				return False
		return True


def main() -> None:
	recorder = InfraredRecoder()

	while True:
		recorder.record()


if __name__ == "__main__":
	main()
