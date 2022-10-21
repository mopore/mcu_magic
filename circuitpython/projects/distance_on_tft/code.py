# circup install adafruit_st7789
# circup install adafruit_display_text
# circup install adafruit_display_neopixel

import terminalio
import displayio
import time

import board
import neopixel
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from distance_provider import DistanceProvider


def main() -> None:
    # Release any resources currently in use for the displays
    displayio.release_displays()

    spi = board.SPI()
    tft_cs = board.TFT_CS  # type: ignore
    tft_dc = board.TFT_DC  # type: ignore

    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
    display = ST7789(
        display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53
    )

    FONTSCALE = 8
    text = "Ready!"
    text_area = bitmap_label.Label(terminalio.FONT, text=text)
    text_area.x = 0
    text_area.y = 0
    
    text_width = text_area.width * FONTSCALE 
    scale_group = displayio.Group(
        scale=FONTSCALE,
        x=display.width // 2 - text_width // 2,
        y=display.height // 2,
    )
    scale_group.append(text_area) 
    display.show(scale_group)
    provider = DistanceProvider()
    
    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
    pixel.brightness = 0.03
    white = (255, 255, 255)
    black = (0, 0, 0)

    while True:
        result = provider.get_distance()
        text = "-"
        if result is not None:
            text = f"{result:.0f}"
            pixel.fill(white)
        else:
            pixel.fill(black)
        text_area.text = text
        text_width = text_area.width * FONTSCALE 
        scale_group.x = display.width // 2 - text_width // 2
        
        time.sleep(0.5)


if __name__ == "__main__":
    main()
