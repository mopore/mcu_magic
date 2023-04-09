import time
import wifi
import socketpool
import asyncio

import adafruit_minimqtt.adafruit_minimqtt as mqtt

import jni_wifi


class Credentials:

	def __init__(self, username: str, password: str) -> None:
		self.username = username
		self.password = password


class MqttBrokerInfo:

	def __init__(
		self, 
		ip: str, 
		port: int = 1883, 
		credentials: Credentials | None = None
	) -> None:
		self.ip = ip
		self.port = port
		self.credentials = credentials


class MqttBroker:
	SERVICE_PREFIX = "jniHome/services"
	ALIVE_POSTFIX = "aliveTick"
	COMMAND_POSTFIX = "command"

	ALIVE_VALUE = "ALIVE"
	EXIT_COMMAND = "exit"
	ALIVE_FREQUENCY_SECONDS = 10

	MAX_CONNECTION_ATTEMPTS = 4
	UTF_8_NAME = "UTF-8"

	INITIATING = 0
	OPERATIONAL = 1
	PROBLEM = 2
	REPAIRING = 3
	DEAD = 4

	def __init__(
		self, 
		broker_info: MqttBrokerInfo,
		name: str,
		send_alive: bool = True,
		message_callback=None, 
		topic_subscriptions: list[str] | None = None
	) -> None:
		self._broker_ip = broker_info.ip
		self._broker_port = broker_info.port
		self._broker_credentials = broker_info.credentials
		self._name = name
		self._message_callback = message_callback	
		self._send_alive = send_alive
		self._topic_alive_name = f"{self.SERVICE_PREFIX}/{self._name}/{self.ALIVE_POSTFIX}"
		self._topic_command_name = f"{self.SERVICE_PREFIX}/{self._name}/{self.COMMAND_POSTFIX}"
		if topic_subscriptions is None:
			self._topic_subscriptions = []
		else:
			self._topic_subscriptions = topic_subscriptions

		self._state = self.INITIATING
		self._blocked = True
		self._connected = False
		self._keep_running = True
		self._mqtt_client: mqtt.MQTT | None = None
		self._first_connect = True
		print("Initializing MQTT broker...")
		self.ensure_mqtt_client()
		self.last_alive = 0
	
	def exit(self) -> None:
		self._keep_running = False
		self._state = self.DEAD
		print(f"Exiting MQTT broker at {self._broker_ip}...")
		if self._mqtt_client is not None:
			self._mqtt_client.disconnect()
			self._mqtt_client = None

	def on_connect(self, client, userdata, flags, rc) -> None:
		print(f"Connected to MQTT broker ({self._broker_ip})")
		self._connected = True
	
	def on_disconnect(self, client, userdata, rc) -> None:
		if int(rc) == 0:
			print("Connection to MQTT broker closed.")
		else:
			print(f"Lost connection to MQTT broker ({self._broker_ip}), reason: {rc}")
		self._connected = False
		if self._keep_running:
			self._state = self.PROBLEM
	
	def on_message(self, client: mqtt.MQTT, topic: str, message: str) -> None:
		if topic == self._topic_command_name:
			if message.lower() == self.EXIT_COMMAND:
				print("Broker received exit command.")
				self.exit()
		if self._message_callback is not None:
			self._message_callback(message, topic)
	
	def publish(self, topic: str, message: str) -> None:
		if not self._self_check():
			print("MQTT not operational, not publishing temperature.")
			return
		try:
			self._mqtt_client.publish(topic, message)
		except Exception as e:
			error_message = f"Error publishing on topic {topic}: {e}"
			print(error_message)
			self._state = self.PROBLEM

	def ensure_mqtt_client(self) -> None:
		if self.OPERATIONAL == self._state:
			return  # Connection is already present
		# Not connected to MQTT broker
		connection_attempts = 1
		while not connection_attempts > self.MAX_CONNECTION_ATTEMPTS:
			try:
				if self._state == self.REPAIRING:
					jni_wifi.connect_wifi()

				self._connected = False
				print(f"Connection attempt No. {connection_attempts}")	
				if self._mqtt_client is None:
					pool = socketpool.SocketPool(wifi.radio)
					now = time.time()
					if self._broker_credentials is None:
						self._mqtt_client = mqtt.MQTT(
							client_id=f"{self._name}{now}",
							broker=self._broker_ip, 
							port=self._broker_port,
							socket_pool=pool,
							is_ssl=False,
							keep_alive=30,
						)
					else:
						print(f"Using credentials for user {self._broker_credentials.username}.")
						self._mqtt_client = mqtt.MQTT(
							client_id=f"{self._name}{now}",
							broker=self._broker_ip, 
							port=self._broker_port,
							socket_pool=pool,
							is_ssl=False,
							keep_alive=30,
							username=self._broker_credentials.username,
							password=self._broker_credentials.password,
						)
					self._mqtt_client.on_connect = self.on_connect  # type: ignore
					self._mqtt_client.on_disconnect = self.on_disconnect  # type: ignore
				
				if self._first_connect:
					self._mqtt_client.connect()
				else:
					self._mqtt_client.reconnect()
				self._connected = True
				self._first_connect = False
				for topic in self._topic_subscriptions:
					self._mqtt_client.subscribe(topic)
					print(f"Subscribed to '{topic}'")
				self._mqtt_client.subscribe(self._topic_command_name)
				self._mqtt_client.on_message = self.on_message

				self._state = self.OPERATIONAL
				break  # We are connected
			except Exception as e:
				error_message = f"Could not connect to {self._broker_ip} due to '{e}'"
				"after attempt No. {connection_attempts}"
				print(error_message)
				self._state = self.PROBLEM
			if not self._connected:
				sleep_time = 0
				if connection_attempts == 1:
					sleep_time = 30
				if connection_attempts == 2:
					sleep_time = 120
				if connection_attempts == 3:
					sleep_time = 900
				print(f"Sleeping for {sleep_time} seconds before retrying...")
				time.sleep(sleep_time)
				connection_attempts += 1

		# We should have a connection after 3 attempts and 17+ minutes...
		if not self._connected:
			print("Error: We should have a connection after 3 attempts and 17+ minutes...")
			self._state = self.DEAD
			self.exit()
	
	def _self_check(self) -> bool:
		if self._keep_running is False:
			return False
		if self._state == self.PROBLEM:
			print("Problem detected. Trying to repair...")
			self._state = self.REPAIRING
			self.ensure_mqtt_client()
		if self._state == self.OPERATIONAL:
			return True
		return False
	
	async def loop_async(self):
		while self._keep_running:
			self.loop()
			await asyncio.sleep(0)

	def loop(self):
		if self.DEAD != self._state and self._keep_running:
			try:
				if self._send_alive:
					now = time.monotonic()
					time_passed = now - self.last_alive
					if time_passed > self.ALIVE_FREQUENCY_SECONDS:
						self.publish(self._topic_alive_name, self.ALIVE_VALUE)
						self.last_alive = now
				# Collect potential messages
				if self._self_check():
					try:
						self._mqtt_client.loop()
					except Exception:
						# Can happen if we are not connected
						...
			except Exception as e:
				print(f"Error while looping: {e}")
