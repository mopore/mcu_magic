import jni_wifi
import jni_mqtt_broker

import asyncio


class MqttBridge:

	SERVICE_NAME = "cudaIgnition"

	# Constants - Change depending on environment
	# MQTT_SERVER_IP = "127.0.0.1"  # Quieter2 on home network
	MQTT_SERVER_IP = "192.168.199.119"  # Quieter2 on home network
	# MQTT_SERVER_IP = "10.200.0.6"  # Quieter2 on Wireguard network
	# MQTT_SERVER_IP = "192.168.199.245"  # PD Manajaro laptop on home network

	def __init__(
		self, 
		message_callback=None, 
		subscriptions: list[str] | None = None
	) -> None:
		self._broker = jni_mqtt_broker.MqttBroker(
			self.MQTT_SERVER_IP,
			self.SERVICE_NAME,
			True,
			message_callback,
			subscriptions	
		) 
		self.message_callback = message_callback	
	
	def exit(self) -> None:
		self._broker.exit()
	
	async def loop_async(self):
		await self._broker.loop_async()
	
	def publish(self, topic: str, message: str) -> None:
		self._broker.publish(topic, message)


def test_cb(message: str, topic: str) -> None:
	print(f"Received topic: {topic}, message: {message}")


async def test_publish_after_5_sec(bridge: MqttBridge) -> None:
	await asyncio.sleep(5)
	bridge.publish("testTopic", "testMessage")


async def main() -> None:
	subscriptions = ["testTopic"]
	print("Testing...")
	jni_wifi.connect_wifi()
	bridge = MqttBridge(test_cb, subscriptions)
	bridge_task = asyncio.create_task(bridge.loop_async())
	publish_task = asyncio.create_task(test_publish_after_5_sec(bridge))
	await asyncio.gather(bridge_task, publish_task)


if __name__ == "__main__":
	asyncio.run(main())
