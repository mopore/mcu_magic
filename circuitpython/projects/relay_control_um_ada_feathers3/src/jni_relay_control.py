import board
import digitalio
import time
# The purpose of this project is to control a relay which cuts the power for the raspberry pi
# with the hostname "ho.HomeNeoPi" in case there is a problem.
# Consequently, the raspberry pi will be restarted when the relay functions with a cut-off.
# The power cable for ho.HomePiNeo has to be conneted with the realy on COM  and NC 
# (Normally Closed).


class RelayControl:
	def __init__(self) -> None:
		# UM FeatherS3
		self.relay_pin = digitalio.DigitalInOut(board.IO11)  # type: ignore    
		# Adafruit Feather
		#  self.relay_pin = digitalio.DigitalInOut(board.D13)
		self.relay_pin.direction = digitalio.Direction.OUTPUT

	def turn_on(self) -> None:
		self.relay_pin.value = True

	def turn_off(self) -> None:
		self.relay_pin.value = False

	def turn_on_for(self, seconds: float) -> None:
		self.turn_on()
		time.sleep(seconds)
		self.turn_off()


def main() -> None:
	control = RelayControl()

	print("Turning relay on in 1 second")
	time.sleep(1)
	control.turn_on()
	seconds_to_wait = 10
	print(f"Waiting for {seconds_to_wait} seconds...")
	time.sleep(seconds_to_wait)

	print("Setting relay to off")
	control.turn_off()

	print("Done")


if __name__ == "__main__":
	main()
