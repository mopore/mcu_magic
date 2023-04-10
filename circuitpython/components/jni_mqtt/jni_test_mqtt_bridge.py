import jni_wifi
import asyncio

import jni_mqtt_broker

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise

MQTT_SERVICE_NAME_KEY = "mqtt_service_name"
MQTT_SERVER_KEY = "mqtt_server"
MQTT_USERNAME_KEY = "mqtt_username"
MQTT_PASSWORD_KEY = "mqtt_password"


class TestMqttBridge:

	def __init__(
		self, 
		message_callback=None, 
		subscriptions: list[str] | None = None
	) -> None:
		service_name = secrets[MQTT_SERVICE_NAME_KEY]
		mqtt_server = secrets[MQTT_SERVER_KEY]
		# credentials = jni_mqtt_broker.MqttCredentials(
		# 	secrets[MQTT_USERNAME_KEY], 
		# 	secrets[MQTT_PASSWORD_KEY]
		# )
		# server_info = jni_mqtt_broker.MqttServerInfo(
		# 	mqtt_server,
		# 	1883,
		# 	credentials
		# )

		server_info = jni_mqtt_broker.MqttServerInfo(mqtt_server)

		self._broker = jni_mqtt_broker.MqttBroker(
			server_info,
			service_name,
			True,
			message_callback,
			subscriptions	
		) 
		self.message_callback = message_callback	
	
	def exit(self) -> None:
		self._broker.exit()
	
	async def loop_async(self, time_sleep: float = .1):
		await self._broker.loop_async(time_sleep)
	
	def publish(self, topic: str, message: str) -> None:
		self._broker.publish(topic, message)


def test_cb(message: str, topic: str) -> None:
	print(f"Received topic: {topic}, message: {message}")


async def test_publish_after_5_sec(bridge: TestMqttBridge) -> None:
	await asyncio.sleep(5)
	bridge.publish("testTopic", "testMessage")


async def main() -> None:
	subscriptions = ["testTopic"]
	print("Testing...")
	jni_wifi.connect_wifi()
	bridge = TestMqttBridge(test_cb, subscriptions)
	bridge_task = asyncio.create_task(bridge.loop_async())
	publish_task = asyncio.create_task(test_publish_after_5_sec(bridge))
	await asyncio.gather(bridge_task, publish_task)


if __name__ == "__main__":
	asyncio.run(main())
