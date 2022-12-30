import busio
import board
import time


def main() -> None:
	counter = 0
	print("Writing bytes to UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	while True:
		counter += 1
		data_string = f"Test #{counter}"
		data = bytes(data_string, "utf-8")
		uart.write(data)
		if counter % 10 == 0:
			print(f"10 packages sent. Total {counter}")
		time.sleep(3)


if __name__ == "__main__":
	main()
