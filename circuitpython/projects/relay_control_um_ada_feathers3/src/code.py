# circup install asyncio adafruit_requests adafruit_datetime adafruit_minimqtt

import asyncio
import microcontroller
import time

import jni_wifi
import jni_neo_mqtt_bridge
import jni_relay_control

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise

MQTT_SERVICE_NAME_KEY = "mqtt_service_name"


class CudaIgnition:
	
	def __init__(self) -> None:
		self.relay_control = jni_relay_control.RelayControl()

	def command_cb(self, message: str, topic: str) -> None:
		print(f"Received command: {message}")
		if "ON" == message.upper().strip():
			self.relay_control.turn_on()
		elif "OFF" == message.upper().strip():
			self.relay_control.turn_off()
		else:
			try:
				seconds_to_wait = float(message)
				self.relay_control.turn_on_for(seconds_to_wait)
			except ValueError:
				print(f"Unknown command: {message}")
	

async def main() -> None:
	service_name = secrets[MQTT_SERVICE_NAME_KEY]
	ignition = CudaIgnition()
	subscriptions = [f"jniHome/services/{service_name}/command"]

	print("Starting Cuda Ignition...")
	jni_wifi.connect_wifi()
	mqtt = jni_neo_mqtt_bridge.NeoMqttBridge(service_name, ignition.command_cb, subscriptions)
	mqtt_loop_task = asyncio.create_task(mqtt.loop_async())
	print("Setup complete.")
	try:
		await asyncio.gather(mqtt_loop_task)
	except Exception:
		print(f"Exception in main loop: {Exception}")
		time.sleep(10)
		microcontroller.reset()


if __name__ == "__main__":
	asyncio.run(main())
