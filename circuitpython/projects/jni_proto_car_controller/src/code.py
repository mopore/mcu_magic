# circup install asyncio adafruit_requests adafruit_datetime adafruit_minimqtt

import time
import asyncio
import traceback

import board
import microcontroller
import neopixel

import jni_wifi
import jni_controller
import jni_controller_mqtt_bridge
from jni_global_settings import LED_YELLOW, LED_RED, LED_GREEN, LED_LOW


async def main() -> None:
	MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
	onboard_neo = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=LED_LOW)  # type: ignore

	print("Initializing JNI Proto Car Controller...")
	onboard_neo.fill(LED_YELLOW)

	try:
		try:
			from secrets.jni_secrets import secrets
		except ImportError:
			print("WiFi secrets are kept in secrets.py, please add them there!")
			raise

		service_name = secrets[MQTT_SERVICE_NAME_KEY]
		controller = jni_controller.Controller(service_name)
		jni_wifi.connect_wifi()
		mqtt_bridge = jni_controller_mqtt_bridge.ControllerMqttBridge(
			service_name, 
			controller.mqtt_cb, 
			controller.get_subs()
		)
		controller._mqtt_bridge = mqtt_bridge
		mqtt_loop_task = asyncio.create_task(mqtt_bridge.loop_async())
		car_control_task = asyncio.create_task(controller.loop_async())
		onboard_neo.fill(LED_GREEN)
	except Exception as err:
		print(f"Setup failed: {err}")
		print(traceback.format_exc())
		onboard_neo.fill(LED_RED)
		raise err

	try:
		await asyncio.gather(mqtt_loop_task, car_control_task)
	except Exception as err:
		print(f"Exception in main loop: {err}")
		print(traceback.format_exc())
		onboard_neo.fill(LED_RED)
		time.sleep(10)
		print("Rebooting...")
		microcontroller.reset()  # type: ignore


if __name__ == "__main__":
	asyncio.run(main())
