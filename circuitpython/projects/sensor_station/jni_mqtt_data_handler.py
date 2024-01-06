import time
import board
import neopixel
from digitalio import DigitalInOut, Pull

from jni_data_handler import DataHandler
from jni_sensor_station import SensorData, SensorStation
from jni_wifi import connect_wifi, disconnect_wifi
from jni_mqtt_bridge import MqttBridge


LED_RED = (255, 0, 0)
LED_GREEN = (0, 255, 0)
LED_ORANGE = (255, 165, 0)
LED_BLACK = (0, 0, 0)
BUTTON_YES = False
BUTTON_NO = True


class MqttDataHandler(DataHandler):

	ALIVE_TICK_INTERVAL = 10
	ALIVE_LED_MAX = 5

	def __init__(
		self, bridge: MqttBridge,
		pixel: neopixel.NeoPixel,
		button: DigitalInOut
	) -> None:
		self.bridge = bridge
		self.last_tick = 0
		self.alive_led_counter = 0
		self.pixel = pixel
		self.button = button
		self.show_led = False  # Initially there is no blinking to indicate an active connection
		self.button_ready = True

	def handle(self, sensor_data: SensorData) -> None:
		# Publish data
		if sensor_data.light_level is not None:
			self.bridge.publish_light_level(sensor_data.light_level)
		if sensor_data.motion_event is not None:
			self.bridge.publish_motion(sensor_data.motion_event.new_motion)
		if sensor_data.aq is not None:
			self.bridge.publish_co2(sensor_data.aq.co2)
			self.bridge.publish_humidity(sensor_data.aq.humidity)
			self.bridge.publish_temperature(sensor_data.aq.temperature)

		# Publish alive tick
		now = time.monotonic()
		time_after_tick = now - self.last_tick
		if time_after_tick > self.ALIVE_TICK_INTERVAL:
			self.bridge.publish_alive_tick()
			self.last_tick = now

		# LED control via internal button
		if self.button_ready:
			if BUTTON_YES == self.button.value:
				self.show_led = not self.show_led
				self.button_ready = False
		else:
			if BUTTON_NO == self.button.value:
				self.button_ready = True

		# LED signalization
		if self.bridge.keep_running is True:
			if self.show_led:
				self.alive_led_counter += 1
				if self.alive_led_counter == (self.ALIVE_LED_MAX - 1):
					self.pixel.fill(LED_GREEN)
				if self.ALIVE_LED_MAX == self.alive_led_counter:
					self.alive_led_counter = 0
					self.pixel.fill(LED_BLACK)
		else:
			self.pixel.fill(LED_RED)


def prepare_datahandler(station_name: str) -> MqttDataHandler | None:
	button = DigitalInOut(board.BUTTON)
	button.switch_to_input(pull=Pull.UP)
	pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
	pixel.brightness = 0.03
	try:
		pixel.fill(LED_ORANGE)
		connect_wifi()
	except Exception as e:
		print(f"Could not connect to Wifi: {e}")
		pixel.fill(LED_RED)
		return

	bridge: MqttBridge | None = None
	try:
		bridge = MqttBridge(station_name)
		pixel.fill(LED_GREEN)
	except Exception as e:
		print(f"Could not create bridge to MQTT broker: {e}")
		pixel.fill(LED_RED)
		disconnect_wifi()

	if bridge is not None:
		handler = MqttDataHandler(bridge, pixel, button)
		return handler
	# Leave with None - will never happen at this point...


def main() -> None:
	print("Starting...")
	station = SensorStation()
	mqtt_handler = prepare_datahandler("Test_from_main")
	if mqtt_handler is None:
		print("Could not create a data handler!")
		return

	# Proceeding with a working data handler...
	FREQUENCE_SECS = 0.5
	while True:
		last_time = time.monotonic()
		sensor_data = station.collect_data()
		mqtt_handler.handle(sensor_data)
		time_diff = time.monotonic() - last_time
		time_to_sleep = FREQUENCE_SECS - time_diff
		if time_to_sleep < 0:
			time_to_sleep = 0
			print("Did not have any time to sleep!")
		# print(f"Time difference to sleep: {time_to_sleep:.1f} secs")
		time.sleep(time_to_sleep)


if __name__ == "__main__":
	main()
