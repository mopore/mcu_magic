import busio
import board
import array
import time


def main() -> None:
	counter = 0
	print("Writing bytes to UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	while True:
		counter += 1
		data_string = f"Test #{counter}"
		data = array.array("B", [ord(c) for c in data_string])
		uart.write(data)
		time.sleep(0.5)
		if counter % 10 == 0:
			print(f"10 packages sent. Total {counter}")


if __name__ == "__main__":
	main()
