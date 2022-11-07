import time
import os


def main() -> None:

	filepath = "testfile.txt"
	while True:
		print(f"Checking for file at {filepath}")
		if filepath in os.listdir("/"):
			print(f"File {filepath} is present!")
		else:
			print(f"File {filepath} does not exist")
		print("Waiting 10 seconds for next check...")
		time.sleep(10)


if __name__ == "__main__":
	main()
