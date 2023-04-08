import time
import asyncio
import json

import jni_car_mqtt_bridge
import jni_feathers3
import jni_input_control
import jni_engine_management
from jni_global_settings import BATTERY_CHECK_FREQUENCY_SECONDS, REFRESH_RATE_HZ


def get_battery_info() -> str: 
	on_usbc_power = jni_feathers3.get_vbus_present()
	voltage: float | None = None
	if not on_usbc_power:
		voltage = jni_feathers3.get_battery_voltage()

	json_string = json.dumps({
		"usbPower": True if on_usbc_power else False,
		"voltage": voltage})	
	return json_string


class CarControl:
	
	EXIT_COMMAND = "exit"
	
	def __init__(self, service_name) -> None:
		self.service_name = service_name
		self._keep_running = True
		self.input_control = jni_input_control.InputControl() 
		self.engine_management = jni_engine_management.EngineManagement()
		self.last_battery_check = 0
		self.mqtt_bridge: jni_car_mqtt_bridge.CarMqttBridge | None = None
		self.pub_topic_battery = f"jniHome/services/{self.service_name}/battery"
		self.sub_command_topic = f"jniHome/services/{self.service_name}/command"
		self.sub_input_topic = f"jniHome/services/{self.service_name}/input"
		self.last_battery_check = 0
	
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
				if self.mqtt_bridge is not None:
					self.mqtt_bridge.exit()
		elif topic == self.sub_input_topic:
			self.input_control.take_json_input(message)
		else:
			print(f"Received unknown topic: {topic}")

	async def loop_async(self):
		while self._keep_running:
			self.loop()
			await asyncio.sleep(1 / REFRESH_RATE_HZ)
	
	def loop(self):
		self.input_control.loop()
		x_demand, y_demand = self.input_control.get_demands()
		self.engine_management.loop(x_demand, y_demand)
		self.check_battery()

	def check_battery(self):
		now = time.monotonic()
		if now - self.last_battery_check > BATTERY_CHECK_FREQUENCY_SECONDS:
			battery_info = get_battery_info()
			if self.mqtt_bridge is not None:
				self.mqtt_bridge.publish(self.pub_topic_battery, battery_info)
			self.last_battery_check = now
