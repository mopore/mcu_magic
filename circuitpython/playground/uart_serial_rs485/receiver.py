import busio
import board


STOP_BYTE = 0x7E


def main() -> None:
	print("Waiting for bytes on UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	while True:
		data = uart.read(32)
		if data:
			print()
			chars = []
			for b in data:
				if b == STOP_BYTE:
					print("[Received STOP_BYTE]", end="")
				else:
					print(b, end="")
					chars.append(chr(b))	
			print(f"Received: {chars}", end="")


if __name__ == "__main__":
	main()
