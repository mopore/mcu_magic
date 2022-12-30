import busio
import board
import time


def main() -> None:
	print("Waiting for bytes on UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	while True:
		data = uart.read(128)
		if data:
			data_string = "".join([chr(b) for b in data])
			print(f"Received: {data_string}")

if __name__ == "__main__":
	main()
