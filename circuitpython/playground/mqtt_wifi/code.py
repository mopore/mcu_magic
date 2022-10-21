# See: https://learn.adafruit.com/mqtt-in-circuitpython/connecting-to-a-mqtt-broker
# Install adafruit_minimqtt.adafruit_minimqtt with `circup install adafruit_minimqtt`
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as mqtt
import time
import microcontroller

try:
	from secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


def connect_wifi() -> None:
	if wifi.radio.ap_info is not None:
		print("Already connected!")
		return
	connect_max_time = 30
	connected = False
	connect_start_time = time.monotonic()
	attempts_counter = 0
	while not connected and ((time.monotonic() - connect_start_time) < connect_max_time):
		try:
			print("Connecting to WiFi...")
			if not wifi.radio.enabled:
				wifi.radio.enabled = True
			ssid = secrets['ssid']
			wifi_pwd = secrets['password']
			wifi.radio.connect(ssid, wifi_pwd)	
			connected = True 
			info = wifi.radio.ap_info
			print(f"Connected to {info.ssid}!")
		except ConnectionError as e:
			attempts_counter += 1
	if not connected:	
		print(f"Could not connect to Wifi afer {attempts_counter} attempts!")
		wifi.radio.enabled = False
		raise ConnectionError()


def disconnect_wifi() -> None:
	print("Disconnecting from WiFi...")
	wifi.radio.enabled = False
	print("Disconnected from WiFi!")


class MqttConnection:

	TEST_TOPIC_NAME = "test/mqtt_con_feather_s3"
	MQTT_SERVER_IP = "192.168.199.119"  # Quieter2 on home network

	def __init__(self) -> None:
		# Create a socket pool
		pool = socketpool.SocketPool(wifi.radio)

		# Set up MQTT client
		mqtt_client = mqtt.MQTT(
			client_id=str(time.monotonic()),
			broker=self.MQTT_SERVER_IP, 
			socket_pool=pool, 
			is_ssl=False,
			keep_alive=30,
		)

		# Connect callback handlers to mqtt_client
		mqtt_client.on_message = self.on_message
		mqtt_client.connect()
		self.mqtt_client = mqtt_client
		self.message_received = False

	def on_message(self, client, topic, message):
		print("New message on topic {0}: {1}".format(topic, message))
		self.message_received = True

	def subscribe(self, topic):
		print("Subscribing to topice...")
		self.mqtt_client.subscribe(topic)

	def publish(self, topic, message):
		print("Publishing message...")
		self.mqtt_client.publish(topic, message)

	def disconnect(self):
		print("Disconnecting from MQTT")
		self.mqtt_client.disconnect()


def read_cpu_freq_json() -> str:
	print("Reading CPU frequency...")
	cpu_temp = '{"cpu_freq_mhz": "not readable"}'
	try:
		cpu_temp = f'{{"cpu_freq_mhz": {(microcontroller.cpu.frequency / 1_000_000) }}}'
		print(f"CPU frequency: {cpu_temp}")
	except Exception as e:
		print(f"Unable to read CPU frequency from {microcontroller.chip_id}.")
	return cpu_temp


def main() -> None:
	connect_wifi()
	mqtt_client = MqttConnection()

	mqtt_client.subscribe(MqttConnection.TEST_TOPIC_NAME)
	cpu_temp_json = read_cpu_freq_json()
	mqtt_client.publish(MqttConnection.TEST_TOPIC_NAME, cpu_temp_json)

	while not mqtt_client.message_received:
		time.sleep(0.5)
		print("Waiting for message...")
		try:
			mqtt_client.mqtt_client.loop(0)
		except Exception as e:
			# This is whether related to ESP32-S3, CircuitPython 8 or both...
			print(f"Ignoring an error while looping: {e}")

	print("Confirmation received!")

	print("closing...")
	mqtt_client.disconnect()
	disconnect_wifi()
	

if __name__ == "__main__":
	main()
