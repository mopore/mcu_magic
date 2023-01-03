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

# Declare a 5 element fire palette
palette_all_equal = [
    0xFFFFFF,  # White
    0xffe20b,  # Yellow
    0xFF660b,  # Orange
    0xa70f0d,  # Red
    0x5b2200,  # Brown
]

palette_weighted = [
    (0, 0xFFFFFF),  # White
    (0.05, 0xffe20b),  # Yellow
    (0.2, 0xFF660b),  # Orange
    (0.45, 0xa70f0d),  # Red
    (0.7, 0x5b2200),  # Brown
]

palette = fancy.expand_gradient(palette_weighted, 100)


def fire_led_strip() -> None:
    num_leds = 166
    # The strip is connected with pin14 of the UM FeatherS3
    pixels = neopixel.NeoPixel(board.IO14, num_leds, brightness=0.1, auto_write=False)  # type: ignore

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
