# circup install asyncio adafruit_requests adafruit_datetime adafruit_minimqtt

import time
import asyncio
import traceback

import board
import microcontroller
import neopixel

import jni_wifi
import jni_car_mqtt_bridge
import jni_car_control
from jni_global_settings import LED_YELLOW, LED_RED, LED_GREEN


async def main() -> None:
	MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
	onboard_neo = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=1)  # type: ignore

	print("Initializing JNI Proto Car...")
	onboard_neo.fill(LED_YELLOW)

	try:
		try:
			from secrets.jni_secrets import secrets
		except ImportError:
			print("WiFi secrets are kept in secrets.py, please add them there!")
			raise

		service_name = secrets[MQTT_SERVICE_NAME_KEY]
		car_control = jni_car_control.CarControl(service_name, onboard_neo)
		jni_wifi.connect_wifi()
		mqtt_bridge = jni_car_mqtt_bridge.CarMqttBridge(
			service_name, 
			car_control.mqtt_cb, 
			car_control.get_subs()
		)
		car_control._mqtt_bridge = mqtt_bridge
		mqtt_loop_task = asyncio.create_task(mqtt_bridge.loop_async())
		car_control_task = asyncio.create_task(car_control.loop_async())
		print("Setup complete.")
		onboard_neo.brightness = 0.03
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
