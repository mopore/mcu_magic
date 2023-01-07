# circup install adafruit_debouncer
import board
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Button


def main() -> None:
	BUTTON_YES = False
	BUTTON_NO = True
	# internal_button = DigitalInOut(board.BUTTON)  # Adafruit ESP32-S3 Feather
	internal_button = DigitalInOut(board.IO0)  # UM Feather S3
	internal_button.switch_to_input(pull=Pull.UP)  # Consequently a click appears as "False"

	debounced_button = Button(internal_button, long_duration_ms=500, value_when_pressed=False)	

	print("Press the internal button.")
	while True:
		debounced_button.update()
		if debounced_button.short_count:
			print(f"Button is shortly pressed ({debounced_button.short_count}x)")
		if debounced_button.long_press:
			print("Button pressed long.")


if __name__ == "__main__":
	main()
