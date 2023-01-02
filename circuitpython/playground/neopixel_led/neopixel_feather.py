# Ensure to have "neopixel" installed
# pip3 install circup
# circup install adafruit_neopixel

# https://learn.adafruit.com/adafruit-neopixel-featherwing/pinouts

import time
import board
import neopixel


def main() -> None:
    # The control pin is the 4th farthest from the USB-C connection on the smaller pin row
    control_pin = board.IO38  # type: ignore # For UM Feather S3
    brigtness_level = 0.03  # More is quite bright ;)
    amount_pixels = 32

    led_strip = neopixel.NeoPixel(
        control_pin, 
        amount_pixels, 
        brightness=brigtness_level, 
        auto_write=False
    )

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    grey = (155, 155, 155)
    colors = [red, green, blue, yellow, black, grey]

    print("Firing the NeoPixel Featherwing...")

    while True:
        for color in colors:
            led_strip.fill(color)
            for i in range(10):
                # led_strip.brightness = 0.1 * (i + 1)
                led_strip.show()
                time.sleep(0.05)
        

if __name__ == "__main__":
    main()
