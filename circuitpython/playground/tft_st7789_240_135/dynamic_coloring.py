# circup install adafruit_st7789
# circup install adafruit_display_text


import board
import terminalio
import displayio

# import digitalio
import time
from adafruit_display_text import label
from adafruit_st7789 import ST7789

# First set some parameters used for shapes and text
BORDER = 20
FONTSCALE = 2
BACKGROUND_COLOR = 0x000000  # Just black
FOREGROUND_COLOR_1 = 0xAA0088  # Purple
FOREGROUND_COLOR_2 = 0x8800AA  # Purple
TEXT_COLOR = 0xEEEEEE  # Bright grey

# tft_power = digitalio.DigitalInOut(board.TFT_I2C_POWER)
# tft_power.direction = digitalio.Direction.OUTPUT
# tft_power.value = 1

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.TFT_CS  # type: ignore
tft_dc = board.TFT_DC  # type: ignore

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = ST7789(
    display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53
)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = BACKGROUND_COLOR

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

COLOR_MAX = 20
# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(
    display.width - BORDER * 2, display.height - BORDER * 2, COLOR_MAX
)

inner_palette = displayio.Palette(COLOR_MAX)

for i in range(COLOR_MAX):
    blueish = 40 + (i * 7)
    # blueish = i + 1
    inner_palette[i] = (0, 0, blueish)
print(f"Palette length: {len(inner_palette)}")
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER
)
splash.append(inner_sprite)

# Draw a label
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=TEXT_COLOR)
text_width = text_area.bounding_box[2] * FONTSCALE
text_group = displayio.Group(
    scale=FONTSCALE,
    x=display.width // 2 - text_width // 2,
    y=display.height // 2,
)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

counter = 0
while True:
    time.sleep(0.1)
    text_area.text = f"Counter {counter}"
    index = counter % COLOR_MAX
    inner_bitmap.fill(index)
    counter += 1
