# circup install adafruit_st7789
# circup install adafruit_display_text

import board
import displayio
import time

# import digitalio
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font


def main() -> None:

    DARK_COLOR = 0x000000
    BRIGHT_COLOR = 0xFFFFFF
    # Release any resources currently in use for the displays
    displayio.release_displays()

    spi = board.SPI()
    tft_cs = board.TFT_CS  # type: ignore
    tft_dc = board.TFT_DC  # type: ignore

    display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
    display = ST7789(
        display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53
    )

    font_file_24 = "fonts/RobotoCondensed-Regular-24.pcf"
    custom_font_36 = bitmap_font.load_font(font_file_24)

    main_group = displayio.Group()

    X_START = 20
    x = X_START
    y = 18
    Y_OFFSET = 25

    areas: list[bitmap_label.Label] = []

    first_group = displayio.Group()
    first_group.x = x
    first_group.y = y
    first_label = bitmap_label.Label(custom_font_36, text="First")
    first_group.append(first_label)
    main_group.append(first_group)
    areas.append(first_label)
  
    y += Y_OFFSET
    second_group = displayio.Group()
    second_group.x = x
    second_group.y = y
    second_label = bitmap_label.Label(custom_font_36, text="Second")
    second_group.append(second_label)
    main_group.append(second_group)
    areas.append(second_label)

    y += Y_OFFSET
    third_group = displayio.Group()
    third_group.x = x
    third_group.y = y
    third_label = bitmap_label.Label(custom_font_36, text="Third")
    third_group.append(third_label)
    main_group.append(third_group)
    areas.append(third_label)
   
    y += Y_OFFSET
    fourth_group = displayio.Group()
    fourth_group.x = x
    fourth_group.y = y
    fourth_label = bitmap_label.Label(custom_font_36, text="Fourth")
    fourth_group.append(fourth_label)
    main_group.append(fourth_group)
    areas.append(fourth_label)
    
    y += Y_OFFSET
    fith_group = displayio.Group()
    fith_group.x = x
    fith_group.y = y
    fith_label = bitmap_label.Label(custom_font_36, text="Fith")
    fith_group.append(fith_label)
    main_group.append(fith_group)
    areas.append(fith_label)

    display.show(main_group)

    last_change = 0
    CHANGE_RATE_SECS = 1
    index = 0
    while True:
        now = time.monotonic()
        time_passed = now - last_change
        if time_passed > CHANGE_RATE_SECS:
            areas[index].color = BRIGHT_COLOR
            areas[index].background_color = DARK_COLOR
            index += 1
            if index == len(areas):
                index = 0
            areas[index].color = DARK_COLOR
            areas[index].background_color = BRIGHT_COLOR
            last_change = now


if __name__ == "__main__":
    main()
