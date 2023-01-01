import time
import board
import analogio

LOGIC_VOLTAGE = 3.3
MAX_READING = 65_535


def main() -> None:
	""" We use the FeatherS3 from Unexpected maker. For details also look in Evernote """
	""" Potentiometer: https://cdn-learn.adafruit.com/assets/assets/000/097/844/medium640/circuitpython_QT_Py_Essentials_Analog_In_bb.jpg?1608044740 """
	""" FSR: https://cdn-learn.adafruit.com/assets/assets/000/000/441/original/force___flex_fsrpulldowndia.png?1396763071 """
	""" Tested with power from 3.3 Volt """

	print("Use the potentiometer or FSR...")
	analog_pin = analogio.AnalogIn(board.A6)  # type: ignore	
	while True:
		reading = (analog_pin.value) / MAX_READING * 100
		print(f"Reading: {reading:.0f}", end="\r")
		time.sleep(0.1)


if __name__ == "__main__":
	main()
