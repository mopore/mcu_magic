# circup install adafruit_st7789

"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""
import time
import board
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7789 import ST7789


def main() -> None:
	BORDER_WIDTH = 20
	TEXT_SCALE = 3

	# Release any resources currently in use for the displays
	displayio.release_displays()

	spi = board.SPI()
	# Adafruit Feather names
	# tft_cs = board.D5
	# tft_dc = board.D6
	# # tft_rst = board.D9
	# UM Feather S3 names
	tft_cs = board.IO33  # type: ignore
	tft_dc = board.IO38  # type: ignore
	# tft_rst = board.IO1

	display_bus = displayio.FourWire(
		spi, 
		command=tft_dc, 
		chip_select=tft_cs, 
		# reset=tft_rst
	)

	display = ST7789(display_bus, width=320, height=170, colstart=35, rotation=90)

	# Make the display context
	splash = displayio.Group()
	display.show(splash)

	color_bitmap = displayio.Bitmap(display.width, display.height, 1)
	color_palette = displayio.Palette(1)
	color_palette[0] = 0x00FF00  # Bright Green
	bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
	splash.append(bg_sprite)

	# Draw a smaller inner rectangle
	inner_bitmap = displayio.Bitmap(
		display.width - (BORDER_WIDTH * 2), display.height - (BORDER_WIDTH * 2), 1
	)
	inner_palette = displayio.Palette(1)
	inner_palette[0] = 0xAA0088  # Purple
	inner_sprite = displayio.TileGrid(
		inner_bitmap, pixel_shader=inner_palette, x=BORDER_WIDTH, y=BORDER_WIDTH
	)
	splash.append(inner_sprite)

	# Draw a label
	text_area = label.Label(
		terminalio.FONT,
		text="I am happy!",
		color=0xFFFF00,
		scale=TEXT_SCALE,
		anchor_point=(0.5, 0.5),
		anchored_position=(display.width // 2, display.height // 2),
	)
	splash.append(text_area)

	counter = 1
	CHANGE_FREQ = 1
	last_time = time.monotonic()
	while True:
		now = time.monotonic()
		diff = now - last_time
		if diff > CHANGE_FREQ:
			counter += 1
			last_time = now
			text_area.text = f"Counter: {counter}"


if __name__ == "__main__":
	main()
