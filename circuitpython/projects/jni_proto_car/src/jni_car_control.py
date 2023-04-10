import time
import asyncio
import json
import neopixel

import jni_car_mqtt_bridge
import jni_feathers3
import jni_input_control
import jni_engine_management
import jni_car_sensors
import jni_global_settings as settings


def get_battery_info() -> str: 
	on_usbc_power = jni_feathers3.get_vbus_present()
	voltage: float | None = None
	if not on_usbc_power:
		voltage = jni_feathers3.get_battery_voltage()

	json_string = json.dumps({
		"usbpower": True if on_usbc_power else False,
		"voltage": voltage})	
	return json_string


class CarControl:
	
	EXIT_COMMAND = "exit"
	
	def __init__(
		self,
		service_name: str,
		onboard_neo: neopixel.NeoPixel | None = None,
		dry_mode: bool = False
	) -> None:
		self._service_name = service_name
		self._onboard_neo = onboard_neo
		self._dry_mode = dry_mode
		self._keep_running = True
		self._panic_mode = False
		self._input_control = jni_input_control.InputControl() 
		self._engine_management = jni_engine_management.EngineManagement(dry_mode)
		self._sensors = jni_car_sensors.CarSensors()
		self._last_battery_check = 0
		self._mqtt_bridge: jni_car_mqtt_bridge.CarMqttBridge | None = None
		self._last_battery_check = 0
		self._panic_led_on = False

		self.pub_topic_battery = f"jniHome/services/{self._service_name}/battery"
		self.sub_command_topic = f"jniHome/services/{self._service_name}/command"
		self.sub_input_topic = f"jniHome/services/{self._service_name}/input"
	
	def get_subs(self) -> list[str]:
		subs = [
			self.sub_command_topic,
			self.sub_input_topic
		]
		return subs

	def mqtt_cb(self, message: str, topic: str) -> None:
		if topic == self.sub_command_topic:
			print(f"Received command: {message}")
			if message.strip().lower() == self.EXIT_COMMAND:
				self._keep_running = False
				if self._mqtt_bridge is not None:
					self._mqtt_bridge.exit()
		elif topic == self.sub_input_topic:
			self._input_control.take_mqtt_input(message)
		else:
			print(f"Received unknown topic: {topic}")

	def switch_panic_mode_on(self):
		self._panic_mode = True
		self._engine_management.panic_stop()
		if self._onboard_neo is not None:
			self._onboard_neo.brightness = settings.LED_FULL
			self._panic_led_on = True
	
	def switch_panic_mode_off(self):
		self._engine_management._panic_mode = False
		if self._onboard_neo is not None:
			self._onboard_neo.brightness = settings.LED_LOW
			self._onboard_neo.fill(settings.LED_GREEN)
		self._panic_mode = False

	async def loop_async(self):
		while self._keep_running:
			self._loop()
			await asyncio.sleep(1 / settings.REFRESH_RATE_HZ)
	
	def _loop(self):
		if self._panic_mode:
			self._loop_panic_mode()	
		else:
			self._loop_default()

	def _loop_default(self):
		self._input_control.loop()
		x_demand, y_demand = self._input_control.get_demands()
		self._engine_management.loop(x_demand, y_demand)
		self._loop_battery_check()
		self._sensors.loop()

	def _loop_battery_check(self):
		now = time.monotonic()
		if now - self._last_battery_check > settings.BATTERY_CHECK_FREQUENCY_SECONDS:
			battery_info = get_battery_info()
			if self._mqtt_bridge is not None:
				self._mqtt_bridge.publish(self.pub_topic_battery, battery_info)
			self._last_battery_check = now

	def _loop_panic_mode(self):
		if self._onboard_neo is not None:
			# Blink the onboard LED
			self._panic_led_on = not self._panic_led_on
			if self._panic_led_on:
				self._onboard_neo.fill(settings.LED_RED)
			else:
				self._onboard_neo.fill(settings.LED_BLACK)
