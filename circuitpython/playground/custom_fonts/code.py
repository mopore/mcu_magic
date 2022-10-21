# circup install adafruit_st7789
# circup install adafruit_display_text

# Custom fonts tutorial: https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display?view=all
# (1) Choose and download a font: https://fonts.google.com/ (will be ttf)
# (2) Install and use 'fontforge' to convvert the ttf into bdf
# (3) In fontforge choose Element -> Bitmap Strikes, and set a size
# (3.1) Remove not-used glpyhs!
# (4) File -> Generate Fonts, Choose 'No Outline Font' and hit generate
# (5) Convert bdf to binary pcf with 'bdftopcf'
# Open and use: https://adafruit.github.io/web-bdftopcf/

import board
# import terminalio
import displayio

# import digitalio
from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font


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
    text = "Hello World!"
    font_file_10 = "fonts/RobotoCondensed-Regular-10.pcf"
    font_file_16 = "fonts/RobotoCondensed-Regular-16.pcf"
    font_file_24 = "fonts/RobotoCondensed-Regular-24.pcf"
    font_file_36 = "fonts/RobotoCondensed-Regular-36.pcf"
    custom_font_10 = bitmap_font.load_font(font_file_10)
    custom_font_16 = bitmap_font.load_font(font_file_16)
    custom_font_24 = bitmap_font.load_font(font_file_24)
    custom_font_36 = bitmap_font.load_font(font_file_36)
    text_area_10 = bitmap_label.Label(custom_font_10, text=text)
    text_area_10.y = 10
    text_area_16 = bitmap_label.Label(custom_font_16, text=text)
    text_area_16.y = 26
    text_area_24 = bitmap_label.Label(custom_font_24, text=text)
    text_area_24.y = 50
    text_area_36 = bitmap_label.Label(custom_font_36, text=text)
    text_area_36.y = 86 
    main_group = displayio.Group()
    main_group.append(text_area_10)
    main_group.append(text_area_16)
    main_group.append(text_area_24)
    main_group.append(text_area_36)
    display.show(main_group)

    while True:
        pass


if __name__ == "__main__":
    main()
