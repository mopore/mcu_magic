# See: https://learn.adafruit.com/mqtt-in-circuitpython/connecting-to-a-mqtt-broker
# Install adafruit_minimqtt.adafruit_minimqtt with `circup install adafruit_minimqtt`
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as mqtt
import asyncio

try:
	from secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


def connect_wifi() -> None:
	print("Connecting to WiFi...")
	ssid = secrets['ssid']
	wifi_pwd = secrets['password']
	wifi.radio.connect(ssid, wifi_pwd)	
	print(f"Connected to {ssid}!")


def disconnect_wifi() -> None:
	print("Disconnecting from WiFi...")
	wifi.radio.enabled = False
	print("Disconnected from WiFi!")


class MqttBridge:

	TOPIC_HISTORY_NAME = "jniHome/services/hueBridge/halo/moveHistory"

	def __init__(self, topic_callback) -> None:
		self.keep_running = True
		self.topic_callback = topic_callback
		self.counter = 0
		pool = socketpool.SocketPool(wifi.radio)
		mqtt_server = secrets['mqtt_server']
		mqtt_client = mqtt.MQTT(broker=mqtt_server, socket_pool=pool, is_ssl=False)

		mqtt_client.on_message = self.on_halo_message
		mqtt_client.connect()
		mqtt_client.subscribe(MqttBridge.TOPIC_HISTORY_NAME)
		self.mqtt_client = mqtt_client
		asyncio.create_task(self.run())

	async def run(self):
		while self.keep_running:
			self.mqtt_client.loop()
			await asyncio.sleep(0.5)
		self.mqtt_client.disconnect()

	def on_halo_message(self, client: mqtt.MQTT, topic: str, message: str) -> None:
		self.topic_callback(message)	
		self.counter += 1
		if self.counter == 3:
			self.keep_running = False

	def publish(self, topic: str, message: str) -> None:
		print("Publishing message...")
		self.mqtt_client.publish(topic, message)

	def disconnect(self):
		print("Disconnecting from MQTT")
		self.mqtt_client.disconnect()


async def main():
	connect_wifi()
	mqtt_bridge = MqttBridge(lambda message: print(f"Received message: {message}"))

	while mqtt_bridge.keep_running:
		await asyncio.sleep(1)

	print("Mqtt bridge is done")


if __name__ == "__main__":
	asyncio.run(main())
