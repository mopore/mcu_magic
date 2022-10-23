# circup install adafruit_st7789
# circup install adafruit_display_text
# circup install adafruit_displayio_layout

import time
import board
import terminalio
import displayio

# import digitalio
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_displayio_layout.layouts.page_layout import PageLayout


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

    page1_group = displayio.Group()
    text = "Page 1"
    text_area1 = bitmap_label.Label(terminalio.FONT, text=text)
    text_area1.x = 10
    text_area1.y = 20
    page1_group.append(text_area1)
    
    page2_group = displayio.Group()
    text = "Page 2"
    text_area2 = bitmap_label.Label(terminalio.FONT, text=text)
    text_area2.x = 10
    text_area2.y = 20
    page2_group.append(text_area2)
    
    page3_group = displayio.Group()
    text = "Page 3"
    text_area3 = bitmap_label.Label(terminalio.FONT, text=text)
    text_area3.x = 10
    text_area3.y = 20
    page3_group.append(text_area3)

    page_layout = PageLayout(0, 0)
    page_layout.add_content(page1_group, "1")
    page_layout.add_content(page2_group, "2")
    page_layout.add_content(page3_group, "3")
     
    main_group = displayio.Group()
    main_group.append(page_layout)

    display.show(main_group)

    page_index = 0
    page_names: list[str] = ["1", "2", "3"]
    last_time = time.monotonic()
    SECS_PER_PAGE = 3
    while True:
        time_diff = time.monotonic() - last_time
        if time_diff > SECS_PER_PAGE:
            last_time = time.monotonic()
            page_index += 1
            if page_index == len(page_names):
                page_index = 0
            page_name = page_names[page_index]
            page_layout.show_page(page_name)


if __name__ == "__main__":
    main()
