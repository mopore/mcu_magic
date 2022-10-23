# circup install adafruit_st7789
# circup install adafruit_display_text

import board
import terminalio
import displayio

# import digitalio
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label


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

    text = "Bottom right"
    text_area = bitmap_label.Label(terminalio.FONT, text=text)
    text_area.anchor_point = (1.0, 1.0)  # Grapping the label on the bottom right
    text_area.anchored_position = (display.width, display.height)
    display.show(text_area)

    while True:
        pass


if __name__ == "__main__":
    main()
