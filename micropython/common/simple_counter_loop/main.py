import _thread
import time


counter = 0

def main() -> None:
    global counter
    while True:
        print(f"Counter: {counter}")
        counter = counter + 1
        time.sleep(1)

if __name__ == "__main__":
    main()
