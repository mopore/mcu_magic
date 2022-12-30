import busio
import board
import time

STOP_BYTE_ARRAY = bytes([0x7E])


def main() -> None:
	counter = 0
	print("Writing bytes to UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	while True:
		counter += 1
		data_string = f"Test #{counter}"
		data_bytes = bytes(data_string, "utf-8")

		data_bytes = b"".join([STOP_BYTE_ARRAY, data_bytes, STOP_BYTE_ARRAY])
		print(f"Sending as string: {data_string}")
		print("Bytes", end=": ")
		for byte in data_bytes:
			print(hex(byte), end=" ")
		print()
		uart.write(data_bytes)
		if counter % 10 == 0:
			print(f"10 packages sent. Total {counter}")
		time.sleep(3)


if __name__ == "__main__":
	main()
