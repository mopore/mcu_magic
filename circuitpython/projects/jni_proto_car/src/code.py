# circup install asyncio adafruit_requests adafruit_datetime adafruit_minimqtt

import asyncio
import microcontroller
import time

import jni_wifi
import jni_car_mqtt_bridge
import jni_car_control

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise

MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
	

async def main() -> None:
	service_name = secrets[MQTT_SERVICE_NAME_KEY]
	subs = [f"jniHome/services/{service_name}/command"]
	print("Starting JNI Proto Car...")
	car_control = jni_car_control.CarControl(service_name)
	jni_wifi.connect_wifi()
	mqtt = jni_car_mqtt_bridge.CarMqttBridge(service_name, car_control.command_cb, subs)
	car_control.mqtt = mqtt
	mqtt_loop_task = asyncio.create_task(mqtt.loop_async())
	car_control_task = asyncio.create_task(car_control.loop_async())
	print("Setup complete.")
	try:
		await asyncio.gather(mqtt_loop_task, car_control_task)
	except Exception:
		print(f"Exception in main loop: {Exception}")
		time.sleep(10)
		microcontroller.reset()  # type: ignore


if __name__ == "__main__":
	asyncio.run(main())
