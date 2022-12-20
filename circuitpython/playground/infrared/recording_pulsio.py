
import board
import time
import pulseio


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

	def tick(self) -> None:
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
		print(f"Values: {pulses_list}")
		self.pulse_in.clear()
		self.pulse_in.resume()
		print("\n\nResetting...")


def main() -> None:
	recorder = InfraredRecoder()

	while True:
		recorder.tick()


if __name__ == "__main__":
	main()
