import busio
import board
import time


STOP_BYTE_ARRAY = bytes([0x7E])
PING_ALL_NODES_ARRAY = bytes([0x7E, 0xFF, 0x03, 0xEE, 0xFE, 0x1F, 0xFF, 0x00, 0x15, 
						0x1C, 0x6C, 0x7E])


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
		time.sleep(1)


if __name__ == "__main__":
	main()
