# Ensure to have "neopixel" installed
#
# pip3 install circup
# circup install neopixel
#
# Product description: https://www.adafruit.com/product/4865

import time
import board
import neopixel
from digitalio import DigitalInOut, Pull


def wait_for_internal_button_press() -> None:
    BUTTON_YES = False
    internal_button = DigitalInOut(board.IO0)  # UM Feather S3
    internal_button.switch_to_input(pull=Pull.UP)

    print("This will crash if the strip does not get a 5v/2A+ power supply!")
    print("Press the internal (boot) button to continue...")

    while True:
        if BUTTON_YES == internal_button.value:
            print("Button is pressed")
            break


def fire_led_strip() -> None:
    # The strip is connected with pin14 of the UM FeatherS3
    led_strip = neopixel.NeoPixel(board.IO14, 166, brightness=0.5, auto_write=False)  # type: ignore
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    grey = (155, 155, 155)
    colors = [red, green, blue, yellow, black, grey]

    print("Firing the NeoPixel...")
    while True:
        for color in colors:
            led_strip.fill(color)
            for i in range(5):
                led_strip.brightness = 0.1 * ((i * 2) + 1)
                led_strip.show()
                time.sleep(0.1)
        

def main() -> None:
    wait_for_internal_button_press()
    fire_led_strip()


if __name__ == "__main__":
    main()
