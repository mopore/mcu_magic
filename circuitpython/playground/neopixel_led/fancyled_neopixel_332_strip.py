# Ensure to have "neopixel" installed
#
# pip3 install circup
# circup install adafruit_neopixel
# circup install adafruit_fancyled
#
# Product description: https://www.adafruit.com/product/4865

import board
import neopixel
import adafruit_fancyled.adafruit_fancyled as fancy

# Declare a 6-element RGB rainbow palette
palette = [
    fancy.CRGB(1.0, 0.0, 0.0),  # Red
    0xFF660b,  # Orange
    fancy.CRGB(0.5, 0.5, 0.0),  # Yellow
    0xFFFFFF,  # White
]


def fire_led_strip() -> None:
    num_leds = 166
    # The strip is connected with pin14 of the UM FeatherS3
    pixels = neopixel.NeoPixel(board.IO14, num_leds, brightness=0.25, auto_write=False)  # type: ignore

    offset = 0  # Positional offset into color palette to get it to 'spin'

    while True:
        for i in range(num_leds):
            # Load each pixel's color from the palette using an offset, run it
            # through the gamma function, pack RGB value and assign to pixel.
            color = fancy.palette_lookup(palette, offset + i / num_leds)
            # color = fancy.gamma_adjust(color, brightness=0.25)
            pixels[i] = color.pack()
        pixels.show()

        # offset += 0.02  # Bigger number = faster spin
        offset += 0.1  # Bigger number = faster spin
        

def main() -> None:
    fire_led_strip()


if __name__ == "__main__":
    main()
