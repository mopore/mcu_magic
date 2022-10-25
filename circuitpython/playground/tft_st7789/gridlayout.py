# circup install adafruit_st7789
# circup install adafruit_display_text
# circup install adafruit_displayio_layout

import board
import terminalio
import displayio
import time

# import digitalio
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout


def create_text_label(label: str) -> bitmap_label.Label:
    text_area = bitmap_label.Label(terminalio.FONT, text=label)
    return text_area


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

    main_group = displayio.Group()

    grid_layout = GridLayout(x=0, y=0, grid_size=(1, 5), width=display.width, height=display.height)
    
    for i in range(5):
        text = f"Item No. {i+1}"
        label = create_text_label(text)
        grid_layout.add_content(label, (0, i), cell_size=(1, 1))
    
    main_group.append(grid_layout)    
    
    display.show(main_group)

    last_change = 0
    CHANGE_RATE_SECS = 1
    while True:
        now = time.monotonic()
        time_passed = now - last_change
        if time_passed > CHANGE_RATE_SECS:
            ...


if __name__ == "__main__":
    main()
