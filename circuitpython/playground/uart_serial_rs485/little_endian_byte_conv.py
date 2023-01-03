def main() -> None:
	# The following bytes come as a byte array in little endian format via the network
	# Since the default on a Circuitpython MCU is big endian the conversion need to to
	# respect the little endian source.
	data_bytes = bytes([0x00, 0x0E, 0x27, 0x07])
	# data_bytes = bytearray([0x00, 0x0E, 0x27, 0x07])  # Needs CircuitPython 8
	# data_bytes = b'\x00\x0E\x27\x07'
	value = int.from_bytes(data_bytes, 'little')
	print(f"The value is {value} w/h.")


if __name__ == "__main__":
	main()
