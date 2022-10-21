import time
import board
import neopixel

from jni_data_handler import DataHandler
from jni_sensor_station import SensorData, SensorStation
from jni_motion_handler import MotionHandler, MotionEventReceiver
from jni_wifi import connect_wifi, disconnect_wifi
from jni_mqtt_bridge import MqttBridge


RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)


class ThisMotionEventReceiver(MotionEventReceiver):
	
	NEW_MOTION = True
	MOTION_GONE = False

	def __init__(self, bridge: MqttBridge) -> None:
		self.bridge = bridge

	def on_new_motion(self) -> None:
		self.bridge.publish_motion(self.NEW_MOTION)

	def on_motion_gone(self) -> None:
		self.bridge.publish_motion(self.MOTION_GONE)


class MqttDataHandler(DataHandler):

	ALIVE_TICK_INTERVAL = 10
	ALIVE_LED_MAX = 20

	def __init__(self, bridge: MqttBridge, pixel: neopixel.NeoPixel) -> None:
		self.motionHandler = MotionHandler(ThisMotionEventReceiver(bridge))
		self.bridge = bridge
		self.last_tick = 0
		self.alive_led_counter = 0
		self.pixel = pixel

	def handle(self, sensor_data: SensorData) -> None:
		self.motionHandler.handle_distance_data(sensor_data.distance)
		self.bridge.publish_light_level(sensor_data.light_level)

		if sensor_data.aq is not None:
			self.bridge.publish_co2(sensor_data.aq.co2)
			self.bridge.publish_humidity(sensor_data.aq.humidity)
			self.bridge.publish_temperature(sensor_data.aq.temperature)

		now = time.monotonic()
		time_after_tick = now - self.last_tick
		if time_after_tick > self.ALIVE_TICK_INTERVAL:
			self.bridge.publish_alive_tick()
			self.last_tick = now

		if self.bridge.keep_running is True:
			self.alive_led_counter += 1
			if self.alive_led_counter == (self.ALIVE_LED_MAX - 1):
				self.pixel.fill(GREEN)
			if self.ALIVE_LED_MAX == self.alive_led_counter:
				self.alive_led_counter = 0
				self.pixel.fill(BLACK)
		else:
			self.pixel.fill(RED)


def prepare_datahandler() -> MqttDataHandler | None:
	pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
	pixel.brightness = 0.03
	try:
		pixel.fill(ORANGE)
		connect_wifi()
	except Exception as e:
		print(f"Could not connect to Wifi: {e}")
		pixel.fill(RED)
		return

	bridge: MqttBridge | None = None
	try:
		bridge = MqttBridge()
		pixel.fill(GREEN)
	except Exception as e:
		print(f"Could not create bridge to MQTT broker: {e}")
		pixel.fill(RED)
		disconnect_wifi()
	
	if bridge is not None:
		handler = MqttDataHandler(bridge, pixel)
		return handler
	# Leave with None - will never happen at this point...


def main() -> None:
	print("Starting...")
	station = SensorStation()
	mqtt_handler = prepare_datahandler()
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
