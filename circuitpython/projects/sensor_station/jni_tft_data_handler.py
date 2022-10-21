# import terminalio
import displayio
import time
import board

from adafruit_st7789 import ST7789
from adafruit_display_text import bitmap_label
from adafruit_bitmap_font import bitmap_font

from jni_data_handler import DataHandler
from jni_sensor_station import SensorData, SensorStation
from jni_aq_provider import Airquality


class TftDataHandler(DataHandler):

	FONTSCALE = 1

	def __init__(self) -> None:
		# Release any resources currently in use for the displays
		displayio.release_displays()

		spi = board.SPI()
		tft_cs = board.TFT_CS  # type: ignore
		tft_dc = board.TFT_DC  # type: ignore

		display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
		display = ST7789(
			display_bus, rotation=270, width=240, height=135, rowstart=40, colstart=53
		)

		text = "Setting everything up..."
		
		# # Custom Font file...
		font_file = "fonts/RobotoCondensed-Regular-16.pcf"
		custom_font = bitmap_font.load_font(font_file)
		# text_area = bitmap_label.Label(terminalio.FONT, text=text)
		text_area = bitmap_label.Label(custom_font, text=text)
		text_area.x = 0
		text_area.y = 10

		# text_width = text_area.width * self.FONTSCALE 
		display.show(text_area)
		self.text_area = text_area
		self.display = display
		self.old_aq: Airquality | None = None
		self.last_draw = time.monotonic()

	def handle(self, sensor_data: SensorData) -> None:
		time_passed = time.monotonic() - self.last_draw
		if time_passed > 1:
			distance_text = "-"
			if sensor_data.distance is not None:
				distance_text = f"{sensor_data.distance:.1f}"
			text = f"Distance: {distance_text} cm *"
			text = f"{text}\nLight Level: {sensor_data.light_level:.1f} lm *"
			if sensor_data.aq is not None:
				text = f"{text}\nCO2: {sensor_data.aq.co2:.1f} ppm *"
				text = f"{text}\nTemperature: {sensor_data.aq.temperature:.1f} C *"
				text = f"{text}\nHumidity: {sensor_data.aq.humidity:.1f}% *"
				self.old_aq = sensor_data.aq
			else:
				if self.old_aq is not None:
					text = f"{text}\nCO2: {self.old_aq.co2:.1f} ppm"
					text = f"{text}\nTemp: {self.old_aq.temperature:.1f} C"
					text = f"{text}\nHumidity: {self.old_aq.humidity:.1f}%"

			self.text_area.text = text
			# text_width = self.text_area.width * self.FONTSCALE 
			# self.scale_group.x = self.display.width // 2 - text_width // 2
			self.last_draw = time.monotonic()
		else:
			if sensor_data.aq is not None:
				self.old_aq = sensor_data.aq


def main() -> None:
	print("Starting...")
	station = SensorStation()
	tft_handler = TftDataHandler()

	FREQUENCE_SECS = 1
	while True:
		last_time = time.monotonic()
		sensor_data = station.collect_data()
		tft_handler.handle(sensor_data)	
		time_diff = time.monotonic() - last_time
		time_to_sleep = FREQUENCE_SECS - time_diff
		if time_to_sleep < 0:
			time_to_sleep = 0
			print("Did not have any time to sleep!")
		# print(f"Time difference to sleep: {time_to_sleep:.1f} secs")
		time.sleep(time_to_sleep)


if __name__ == "__main__":
	main()
