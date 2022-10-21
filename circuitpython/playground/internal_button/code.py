import board
from digitalio import DigitalInOut, Pull


def main() -> None:
	BUTTON_YES = False
	BUTTON_NO = True
	internal_button = DigitalInOut(board.BUTTON)  # Adafruit ESP32-S3 Feather
	internal_button.switch_to_input(pull=Pull.UP)

	print("Press the internal button.")

	ready_to_press = True
	while True:
		if ready_to_press:
			if BUTTON_YES == internal_button.value:
				print("Button is pressed")
				ready_to_press = False
		else:
			if BUTTON_NO == internal_button.value:
				print("Button released")
				ready_to_press = True


if __name__ == "__main__":
	main()
