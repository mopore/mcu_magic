import busio
import board


STOP_BYTE = 0x7E


def main() -> None:
	print("Waiting for bytes on UART...")
	uart = busio.UART(tx=board.TX, rx=board.RX, baudrate=19200)
	chars = []
	while True:
		data = uart.read(32)
		if data:
			print()
			for b in data:
				if b == STOP_BYTE:
					# print("\n[Received STOP_BYTE]")
					if len(chars) > 0:
						word = "".join(chars)
						print(f"\n\nReceived: {word}\n")
						chars = []
				else:
					print(hex(b), end=" ")
					chars.append(chr(b))	


if __name__ == "__main__":
	main()
