# circup install adafruit_vl53l1x adafruit_pct2075 adafruit_neopixel asyncio 
# circup install adafruit_datetime adafruit_minimqtt
import asyncio

import jni_wifi
import jni_wardrobe_main
import jni_wardrobe_mqtt_bridge


async def main() -> None:
	print("Starting...")
	MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
	try:
		from secrets.jni_secrets import secrets
	except ImportError:
		print("WiFi secrets are kept in secrets.py, please add them there!")
		raise

	jni_wifi.connect_wifi() 
	service_name = secrets[MQTT_SERVICE_NAME_KEY]
	mqtt_bridge = jni_wardrobe_mqtt_bridge.WardrobeMqttBridge(service_name)
	mqtt_loop_task = asyncio.create_task(
		mqtt_bridge.loop_async(loop_sleeps=1)
	)
	main = jni_wardrobe_main.WardrobeMain(mqtt_bridge)
	main_task = asyncio.create_task(main.loop_async())
	await asyncio.gather(mqtt_loop_task, main_task) 

if __name__ == "__main__":
	asyncio.run(main())
