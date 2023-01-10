import board
import digitalio
import time


def main() -> None:
	led = digitalio.DigitalInOut(board.IO5)  # type: ignore
	led.direction = digitalio.Direction.OUTPUT	
	led.value = True
	time.sleep(3)


if __name__ == "__main__":
	main()
