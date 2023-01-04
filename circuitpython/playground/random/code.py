import random


def main() -> None:
	for _ in range(100):
		value: int = random.randint(0, 5)
		print(f"Random value between 0 and 5 inclusive: {value}")


if __name__ == "__main__":
	main()
