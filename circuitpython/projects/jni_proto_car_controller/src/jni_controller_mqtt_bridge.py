import jni_mqtt_broker

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


MQTT_SERVER_KEY = "mqtt_server"


class ControllerMqttBridge:

	def __init__(
		self, 
		service_name: str,
		message_callback=None, 
		subscriptions: list[str] | None = None
	) -> None:
		mqtt_server = secrets[MQTT_SERVER_KEY]
		server_info = jni_mqtt_broker.MqttServerInfo(mqtt_server)
		self._broker = jni_mqtt_broker.MqttBroker(
			server_info,
			service_name,
			True,
			message_callback,
			subscriptions	
		) 
		self.message_callback = message_callback	
	
	def publish_xy(self, json_string: str) -> None:
		self._broker.publish("jniHome/services/jniProtoCar/input", json_string)
	
	def exit(self) -> None:
		self._broker.exit()
	
	async def loop_async(self):
		await self._broker.loop_async()
	
	def publish(self, topic: str, message: str) -> None:
		self._broker.publish(topic, message)
