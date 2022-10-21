import board
import digitalio
import time

# See: https://images.squarespace-cdn.com/content/v1/5a8cc639a803bbfaa029615a/d12e60b8-9864-4b4b-8913-f9fc1fcf80f1/pins_feathers3.jpg?format=1500w


def main() -> None:
    #  led = digitalio.DigitalInOut(board.A6)  # Ada
    led = digitalio.DigitalInOut(board.IO1)  # UM
    led.direction = digitalio.Direction.OUTPUT
    print("Starting to blink...")
    while True:
        led.value = True
        time.sleep(0.5)
        led.value = False
        time.sleep(0.5)


if __name__ == "__main__":
    main()  
