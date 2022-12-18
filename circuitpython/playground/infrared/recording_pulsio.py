
import board
from digitalio import DigitalInOut, Pull
import pulseio

BUTTON_YES = False
BUTTON_NO = True


class InfraredRecoder():

	def __init__(
		self,
	) -> None:
		self.last_tick = 0
		self.button_ready = True
		self.recording = False
		
		# Preparing IR receiver
		self.pulses = pulseio.PulseIn(board.IO6, maxlen=200, idle_state=True)  # type: ignore  
		self.pulses.pause()

		# Preparing the internal button to start and stop recordings
		# button = DigitalInOut(board.BUTTON)  # Adafruit ESP32-S3 Feather
		button = DigitalInOut(board.IO0)  # UM Feather S3
		button.switch_to_input(pull=Pull.UP)
		self.button = button
		print("Press internal button to start recording...")

	def tick(self) -> None:
		if self.button_ready:
			if BUTTON_YES == self.button.value:
				self.recording = not self.recording
				self.button_ready = False
				if self.recording:
					self.start_recording()
				else:
					self.stop_recording()
		else:
			if BUTTON_NO == self.button.value:
				self.button_ready = True

	def start_recording(self) -> None:
		print("Starting recording...")
		self.pulses.clear()
		self.pulses.resume()

	def stop_recording(self) -> None:
		print("Stopping recording...")
		self.pulses.pause()
		print(f"Lenght of recorded pulses: {len(self.pulses)}")


def main() -> None:
	recorder = InfraredRecoder()

	while True:
		recorder.tick()


if __name__ == "__main__":
	main()
