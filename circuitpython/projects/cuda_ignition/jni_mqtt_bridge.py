import time
import wifi
import socketpool

import asyncio
import adafruit_minimqtt.adafruit_minimqtt as mqtt

import jni_wifi


class MqttBridge:

	SERVICE_NAME = "cudaIgnition"
	TOPIC_COMMAND_NAME = f"jniHome/services/{SERVICE_NAME}/command"
	TOPIC_ALIVE_NAME = f"jniHome/services/{SERVICE_NAME}/aliveTick"

	# Constants - Change depending on environment
	MQTT_SERVER_IP = "192.168.199.119"  # Quieter2 on home network
	# MQTT_SERVER_IP = "10.200.0.6"  # Quieter2 on Wireguard network
	# MQTT_SERVER_IP = "192.168.199.214"  # PD Manajaro laptop on home network

	ALIVE_VALUE = "ALIVE"
	ALIVE_FREQUENCY_SECONDS = 10

	MAX_CONNECTION_ATTEMPTS = 4
	UTF_8_NAME = "UTF-8"

	INITIATING = 0
	OPERATIONAL = 1
	PROBLEM = 2
	REPAIRING = 3
	DEAD = 4

	def __init__(self, bridge_name, topic_callback) -> None:
		self.station_name = bridge_name
		self.topic_callback = topic_callback	
		self.state = self.INITIATING
		self.blocked = True
		self.connected = False
		self.keep_running = True
		self.mqtt_client: mqtt.MQTT | None = None
		self.first_connect = True
		self.ensure_mqtt_client()
		self.last_alive = 0
	
	def exit(self) -> None:
		self.state = self.DEAD
		print(f"Exiting MQTT broker at {self.MQTT_SERVER_IP}...")
		self.keep_running = False
		if self.mqtt_client is not None:
			self.mqtt_client.disconnect()
			self.mqtt_client = None

	def on_connect(self, client, userdata, flags, rc) -> None:
		print(f"Connected to MQTT server ({self.MQTT_SERVER_IP})")
		self.connected = True
	
	def on_disconnect(self, client, userdata, rc) -> None:
		if int(rc) == 0:
			print("Connection to MQTT server closed.")
		else:
			print(f"Lost connection to MQTT server ({self.MQTT_SERVER_IP}), reason: {rc}")
		self.connected = False
	
	def on_message(self, client: mqtt.MQTT, topic: str, message: str) -> None:
		self.topic_callback(message)

	def ensure_mqtt_client(self) -> None:
		if self.OPERATIONAL == self.state:
			return  # Connection is already present
		# Not connected to MQTT broker
		connection_attempts = 1
		while not connection_attempts > self.MAX_CONNECTION_ATTEMPTS:
			try:
				if self.state == self.REPAIRING:
					jni_wifi.connect_wifi()

				# print(f"Connection attempt No. {connection_attempts}")	
				if self.mqtt_client is None:
					pool = socketpool.SocketPool(wifi.radio)
					now = time.time()
					self.mqtt_client = mqtt.MQTT(
						client_id=f"{self.station_name}{now}",
						broker=self.MQTT_SERVER_IP, 
						socket_pool=pool,
						is_ssl=False,
						keep_alive=30,
					)
					self.mqtt_client.on_connect = self.on_connect  # type: ignore
					self.mqtt_client.on_disconnect = self.on_disconnect  # type: ignore
				# else: Use existing client
				
				if self.first_connect:
					self.mqtt_client.connect()
				else:
					self.mqtt_client.reconnect()
				self.connected = True
				self.first_connect = False
				self.mqtt_client.subscribe(self.TOPIC_COMMAND_NAME)
				print(f"Subscribed to '{self.TOPIC_COMMAND_NAME}'")
				self.mqtt_client.on_message = self.on_message

				self.state = self.OPERATIONAL
				break  # We are connected
			except Exception as e:
				error_message = f"Could not connect to {self.MQTT_SERVER_IP} "
				"after attempt No. {connection_attempts}"
				print(error_message)
				self.state = self.PROBLEM
			if not self.connected:
				if connection_attempts == 1:
					time.sleep(30)
				if connection_attempts == 2:
					time.sleep(120)
				if connection_attempts == 3:
					time.sleep(900)
				connection_attempts += 1

		# We should have a connection after 3 attempts and 17+ minutes...
		if not self.connected:
			print("Error: We should have a connection after 3 attempts and 17+ minutes...")
			self.state = self.DEAD
			self.exit()
	
	def _self_check(self) -> bool:
		if self.state == self.PROBLEM:
			print("Problem detected. Trying to repair...")
			self.state = self.REPAIRING
			self.ensure_mqtt_client()
		if self.state != self.OPERATIONAL:
			return False
		return True
	
	def _handle_error(self, error_message: str) -> None:
		print(error_message)
		self.state = self.PROBLEM
		self.blocked = True
	
	async def loop(self):
		while self.DEAD != self.state:
			try:
				now = time.monotonic()
				time_passed = now - self.last_alive
				if time_passed > self.ALIVE_FREQUENCY_SECONDS:
					if not self._self_check():
						print("MQTT not operational, postponing alive tick...")
					else:
						self.mqtt_client.publish(self.TOPIC_ALIVE_NAME, self.ALIVE_VALUE)
						self.last_alive = now
				if self.OPERATIONAL == self.state:
					self.mqtt_client.loop()
				await asyncio.sleep(0)
			except Exception as e:
				# This is whether related to ESP32-S3, CircuitPython 8 or both...
				print(f"Ignoring an error while looping: {e}")
