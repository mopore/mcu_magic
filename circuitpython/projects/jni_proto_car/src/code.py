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
import jni_input_socket
from jni_global_settings import LED_YELLOW, LED_RED, LED_GREEN, REFRESH_RATE_HZ

TENTH_SEC = 1
SEC_INTERVALL = 1


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

		jni_wifi.connect_wifi()
		service_name = secrets[MQTT_SERVICE_NAME_KEY]
		car_control = jni_car_control.CarControl(service_name, onboard_neo)
		mqtt_bridge = jni_car_mqtt_bridge.CarMqttBridge(
			service_name, 
			car_control.mqtt_cb, 
			car_control.get_subs()
		)
		car_control._mqtt_bridge = mqtt_bridge
		socket = jni_input_socket.InputSocket()
		car_control._input_control.set_input_socket(socket)
		
		# Collect all tasks.
		mqtt_loop_task = asyncio.create_task(mqtt_bridge.loop_async(SEC_INTERVALL))
		car_control_task = asyncio.create_task(
			car_control.loop_async(TENTH_SEC)
		)
		read_socket_task = asyncio.create_task(socket.loop_async(TENTH_SEC))

		print("Setup complete.")
		onboard_neo.brightness = 0.03
		onboard_neo.fill(LED_GREEN)
	except Exception as err:
		print(f"Setup failed: {err}")
		print(traceback.format_exc())
		onboard_neo.fill(LED_RED)
		raise err

	try:
		await asyncio.gather(mqtt_loop_task, car_control_task, read_socket_task)
	except Exception as err:
		print(f"Exception in main loop: {err}")
		print(traceback.format_exc())
		onboard_neo.fill(LED_RED)
		time.sleep(10)
		print("Rebooting...")
		microcontroller.reset()  # type: ignore


if __name__ == "__main__":
	asyncio.run(main())
