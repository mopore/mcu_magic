# circup install adafruit_pct2075
import time
import board
import adafruit_pct2075


def main() -> None:
	# i2c = board.I2C()
	i2c = board.STEMMA_I2C()  # type: ignore # For Adafruit QTPy ESP32-S3
	pct = adafruit_pct2075.PCT2075(i2c)
	
	print("Starting...")
	while True:                            # Repeat forever...
		temp = pct.temperature
		print(f"Temperature: {temp:.1f} °C", end="\r")
		time.sleep(2)


if __name__ == "__main__":
	main()
