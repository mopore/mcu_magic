# Ensure to have "neopixel" installed
# pip3 install circup
# circup install neopixel

import time
import board
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
pixel.brightness = 0.03

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
orange = (255, 165, 0)
black = (0, 0, 0)
colors = [red, green, blue, white, orange, black]

print("Firing the NeoPixel...")
while True:
    for color in colors:
        pixel.fill(color)
        time.sleep(0.2)
