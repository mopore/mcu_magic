# circup install adafruit_ssd1680
# circup install adafruit_display_text

import time
import board
import displayio
import adafruit_ssd1680
from adafruit_display_text import label
import terminalio


WIDTH = 250
HEIGHT = 130


def rebuild_group(g: displayio.Group, counter: int) -> None:

	while len(g) > 0:
		g.pop()

	color_palette = displayio.Palette(1)
	color_palette[0] = 0xFFFFFF  # White
	lrg_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
	lrg_square = displayio.TileGrid(lrg_bitmap, pixel_shader=color_palette, x=0, y=0)
	g.append(lrg_square) 

	BLACK = 0x000000
	text = f"Hello {counter}"
	text_label = label.Label(terminalio.FONT, text=text, color=BLACK, x=0, y=30)
	g.append(text_label)


def main() -> None:
	displayio.release_displays()

	# This pinout works on a Metro M4 and may need to be altered for other boards.
	spi = board.SPI()  # Uses SCK and MOSI
	epd_cs = board.D9
	epd_dc = board.D10
	epd_reset = None  # Set to None for FeatherWing
	epd_busy = None  # Set to None for FeatherWing

	display_bus = displayio.FourWire(
		spi, command=epd_dc, chip_select=epd_cs, reset=epd_reset, baudrate=1000000
	)
	time.sleep(1)

	display = adafruit_ssd1680.SSD1680(
		display_bus,
		width=WIDTH,
		height=HEIGHT,
		busy_pin=epd_busy,
		highlight_color=0xFF0000,
		rotation=270,
	)

	counter = 0
	g = displayio.Group()
	rebuild_group(g, counter)
	display.show(g)

	while True:
		display.refresh()
		time.sleep(180)
		counter += 1
		rebuild_group(g, counter)
		print("refreshed")


if __name__ == "__main__":
	main()
