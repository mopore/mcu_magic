import json

from adafruit_datetime import datetime
import jni_mqtt_broker

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


MQTT_SERVER_KEY = "mqtt_server"
DOOR_MOTION_TOPIC = "jniHome/objects/sensor_wardrobe/events/motion"
TEMPARTURE_TOPIC = "jniHome/objects/sensor_wardrobe/events/temperature"


class WardrobeMqttBridge:

	def __init__(
		self, 
		service_name: str,
	) -> None:
		mqtt_server = secrets[MQTT_SERVER_KEY]
		server_info = jni_mqtt_broker.MqttServerInfo(mqtt_server)
		self._broker = jni_mqtt_broker.MqttBroker(
			server_info,
			service_name,
			True,
		) 
	
	async def loop_async(self, loop_sleeps: float = 1):
		await self._broker.loop_async(loop_sleeps)
	
	def update_door_state(self, open: bool) -> None:
		now = datetime.now()
		javascript_date_string = now.isoformat()
		json_string = json.dumps({"door_open": open, "utcTime": javascript_date_string})
		self._broker.publish(DOOR_MOTION_TOPIC, json_string)
	
	def update_temperature(self, temperature: float) -> None:
		now = datetime.now()
		javascript_date_string = now.isoformat()
		json_string = json.dumps({"temperature": temperature, "utcTime": javascript_date_string})
		self._broker.publish(TEMPARTURE_TOPIC, json_string) 

	def publish(self, topic: str, message: str) -> None:
		self._broker.publish(topic, message)
