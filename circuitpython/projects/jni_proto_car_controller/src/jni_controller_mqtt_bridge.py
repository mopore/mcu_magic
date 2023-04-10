import jni_mqtt_broker
from jni_global_settings import TARGET_TOPIC

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
	
	def publish_xy_deprecated(self, x: int, y: int) -> None:
		raw_string = f"{x},{y}" 
		self._broker.publish(TARGET_TOPIC, raw_string)
		raise Exception("Deprecated")
	
	def exit(self) -> None:
		self._broker.exit()
	
	async def loop_async(self, loop_sleeps: float = 1):
		await self._broker.loop_async(loop_sleeps)
	
	def publish(self, topic: str, message: str) -> None:
		self._broker.publish(topic, message)
