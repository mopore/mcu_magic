# See: https://learn.adafruit.com/mqtt-in-circuitpython/connecting-to-a-mqtt-broker
# Install adafruit_minimqtt.adafruit_minimqtt with `circup install adafruit_minimqtt`
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as mqtt
import time
import microcontroller
import ssl
import gc

gc.collect()

try:
	from secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


def connect_wifi() -> None:
	if wifi.radio.enabled:
		print("Already connected...")
		return
	connect_max_time = 30
	connected = False
	connect_start_time = time.monotonic()
	attempts_counter = 0
	while not connected and ((time.monotonic() - connect_start_time) < connect_max_time):
		try:
			print("Connecting to WiFi...")
			wifi.radio.enabled = True
			ssid = secrets['ssid']
			wifi_pwd = secrets['password']
			wifi.radio.connect(ssid, wifi_pwd)	
			connected = True 
			print(f"Connected to {ssid}!")
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

	CERT_FILE = "/moisture_thing_1.cert.pem"
	KEY_FILE = "/moisture_thing_1.private.key"
	ROOT_CERT_FILE = "/root-CA.crt"
	MQTT_CLIENT_ID = "basicPubSub"
	MQTT_PORT = 8883
	TEST_TOPIC_NAME = "sdk/test/Python"

	def __init__(self) -> None:
		print("Reading ca cert file...")
		with open(self.ROOT_CERT_FILE, "r") as f: 
			ca_data = f.read()
		# print(f"Cert file {ca_data}")

		print("Building SSL context...")
		pool = socketpool.SocketPool(wifi.radio)
		ssl_context = ssl.create_default_context()
		print("Verify location with root ca...")

		ssl_context.load_verify_locations(cadata=ca_data)

		# The following is not supported... This will prevent us to properly use TLS
		# ssl_context.load_cert_chain(certfile=self.CERT_FILE, keyfile=self.KEY_FILE)

		# Test if this goeas through
		print("Wrapping the context")
		server_hostname = "a6ygioa4gqbri-ats.iot.eu-central-1.amazonaws.com"
		# ssl_socket = ssl_context.wrap_socket(
		# 	sock=pool, 
		# 	server_hostname=server_hostname
		# )
		# url = "https://{}".format(aws_iot_endpoint)
		# Alternative way without TLS will also not work...
		# alpn_protocol_name_cust_auth = "mqtt" ##
		custom_auth_name = "CustomAuth_up"
		username = "test"
		useridParams = "{}?x-amz-customauthorizer-name={}".format(username, custom_auth_name)
		port = 443

		# Set up MQTT client
		mqtt_client = mqtt.MQTT(
			client_id=self.MQTT_CLIENT_ID,
			broker=server_hostname, 
			port=port,
			ssl_context=ssl_context,
			keep_alive=5000,
			# socket_pool=ssl_socket, 
			socket_pool=pool, 
			is_ssl=True,
			username=useridParams

		)

		# Connect callback handlers to mqtt_client
		mqtt_client.on_message = self.on_message
		print("Trying to connect...")
		mqtt_client.connect()
		print("Connected.")
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
	cpu_freq = '{"cpu_freq_mhz": "not readable"}'
	try:
		cpu_freq = f'{{"cpu_freq_mhz": {(microcontroller.cpu.frequency / 1_000_000) }}}'
		print(f"CPU frequency: {cpu_freq}")
	except Exception as e:
		print(f"Unable to read CPU frequency from {microcontroller.chip_id}.")
	return cpu_freq


def main() -> None:
	connect_wifi()	
	mqtt_client = MqttConnection()
	mqtt_client.subscribe(MqttConnection.TEST_TOPIC_NAME)
	cpu_temp_json = read_cpu_freq_json()
	mqtt_client.publish(MqttConnection.TEST_TOPIC_NAME, cpu_temp_json)

	print("Waiting for message...")
	while not mqtt_client.message_received:
		mqtt_client.mqtt_client.loop()
		time.sleep(0.5)
	print("Confirmation received!")

	mqtt_client.disconnect()
	disconnect_wifi()
	

if __name__ == "__main__":
	main()
