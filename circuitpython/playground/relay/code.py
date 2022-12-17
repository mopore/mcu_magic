import board
import digitalio
from digitalio import DigitalInOut, Pull
import time
# If the relay is unset, the NC pin (Normally Connected) is mechanically 
# connected to COM. NO (Normally Open) is mechanically disconnected.
# When the relay is set, NC becomes disconnected from COM and NO is 
# connected to COM


def main() -> None:

    relay_pin = DigitalInOut(board.IO11)
    relay_pin.direction = digitalio.Direction.OUTPUT

    print("Setting relay to on in 1 second")
    time.sleep(1)
    relay_pin.value = True

    seconds_to_wait = 10
    print(f"Waiting for {5} seconds...")
    time.sleep(seconds_to_wait)

    print("Setting relay to off")
    relay_pin.value = False

    print("Done")
if __name__ == "__main__":
    main()

