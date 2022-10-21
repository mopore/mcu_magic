# Ensure to have "neopixel" installed
# pip3 install circup
# circup install neopixel

import time
import board
import neopixel

# The strip is connected with pin14 of the UM FeatherS3
led_strip = neopixel.NeoPixel(board.IO14, 166, brightness=0.5, auto_write=False)

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
        for i in range(10):
            # led_strip.brightness = 0.1 * (i + 1)
            led_strip.show()
            time.sleep(0.1)
        
