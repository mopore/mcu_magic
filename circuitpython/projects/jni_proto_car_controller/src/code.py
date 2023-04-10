# circup install asyncio adafruit_requests adafruit_datetime adafruit_minimqtt

import time
import asyncio
import traceback

import board
import microcontroller
import neopixel

import jni_wifi
import jni_controller_main
import jni_home_socket
import jni_controller_mqtt_bridge
from jni_global_settings import LED_YELLOW, LED_RED, LED_GREEN, LED_LOW


async def main() -> None:
	print("Initializing JNI Proto Car Controller...")
	MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
	onboard_neo = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=LED_LOW)  # type: ignore
	onboard_neo.fill(LED_YELLOW)

	try:
		try:
			from secrets.jni_secrets import secrets
		except ImportError:
			print("WiFi secrets are kept in secrets.py, please add them there!")
			raise
		service_name = secrets[MQTT_SERVICE_NAME_KEY]

		jni_wifi.connect_wifi()
		home_socket = jni_home_socket.HomeSocket()
		home_socket_task = asyncio.create_task(home_socket.loop_async(.1))
		main = jni_controller_main.ControllerMain(service_name, home_socket)
		mqtt_bridge = jni_controller_mqtt_bridge.ControllerMqttBridge(
			service_name, 
			main.mqtt_cb, 
			main.get_subs()
		)
		mqtt_loop_task = asyncio.create_task(
			mqtt_bridge.loop_async(loop_sleeps=1)
		)
		main._mqtt_bridge = mqtt_bridge

		main_task = asyncio.create_task(
			main.loop_async(loop_sleeps=0)
		)
		onboard_neo.fill(LED_GREEN)
		try:
			await asyncio.gather(mqtt_loop_task, main_task, home_socket_task)
		except Exception as err:
			print(f"Exception in loops: {err}")
			print(traceback.format_exc())
			onboard_neo.fill(LED_RED)
			time.sleep(10)
			print("Rebooting...")
			microcontroller.reset()  # type: ignore
	except Exception as err:
		print(f"Setup failed: {err}")
		onboard_neo.fill(LED_RED)
		raise err


if __name__ == "__main__":
	asyncio.run(main())
