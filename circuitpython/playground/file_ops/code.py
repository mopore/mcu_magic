import time


def main() -> None:

	filepath = "./testfile.txt"
	try:
		print(f"Writing into {filepath}")
		with open(filepath, "a") as filehandler:
			timestamp = time.time()
			print(f"Writing new timestamp: {timestamp}")
			filehandler.write(f"{timestamp}\n")
			filehandler.close()

		print("Reading from file...")
		with open(filepath, "r") as filehandler:
			content = filehandler.read()
			print(f"Start>>>\n{content}")
			print("<<<end")
			filehandler.close()
	except Exception as e:
		print(f"Error writing to {filepath}: {e}")
		print("Ensure to have boot.py copied to flash drive!")	
		print("Ground pin 'A0' to make the drive writable after next boot.")


if __name__ == "__main__":
	main()
