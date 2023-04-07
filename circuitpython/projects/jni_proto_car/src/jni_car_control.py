import asyncio
import jni_car_mqtt_bridge
import feathers3
import json


def get_battery_info() -> str: 
	on_usbc_power = feathers3.get_vbus_present()
	voltage: float | None = None
	if not on_usbc_power:
		voltage = feathers3.get_battery_voltage()

	json_string = json.dumps({
		"usbPower": True if on_usbc_power else False,
		"voltage": voltage})	
	return json_string


class CarControl:
	
	EXIT_COMMAND = "exit"
	BATTERY_CHECK_FREQUENCY_SECONDS = 10
	
	def __init__(self, service_name) -> None:
		self.service_name = service_name
		self._keep_running = True
		self.last_battery_check = 0
		self.mqtt: jni_car_mqtt_bridge.CarMqttBridge | None = None

	def command_cb(self, message: str, topic: str) -> None:
		print(f"Received command: {message}")
		if message.strip().lower() == self.EXIT_COMMAND:
			self._keep_running = False
			if self.mqtt is not None:
				self.mqtt.exit()

	async def loop_async(self):
		while self._keep_running:
			self.loop()
			await asyncio.sleep(self.BATTERY_CHECK_FREQUENCY_SECONDS)
	
	def loop(self):
		battery_info = get_battery_info()
		if self.mqtt is not None:
			self.mqtt.publish(f"jniHome/services/{self.service_name}/battery", battery_info)
