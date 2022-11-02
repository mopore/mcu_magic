import time
import json
import wifi
import socketpool

from adafruit_datetime import datetime
import adafruit_minimqtt.adafruit_minimqtt as mqtt

import jni_wifi


class MqttBridge:

	# Constants - Change depending on environment
	MQTT_SERVER_IP = "192.168.199.119"  # Quieter2 on home network
	# MQTT_SERVER_IP = "10.200.0.6"  # Quieter2 on Wireguard network
	# MQTT_SERVER_IP = "192.168.199.214"  # PD Manajaro laptop on home network

	ALIVE_VALUE = "ALIVE"
	MAX_CONNECTION_ATTEMPTS = 4
	UTF_8_NAME = "UTF-8"

	INITIATING = 0
	OPERATIONAL = 1
	PROBLEM = 2
	REPAIRING = 3
	DEAD = 4

	def __init__(self, station_name) -> None:
		self.station_name = station_name
		self.TOPIC_COMMAND = f"jniHome/services/{station_name}/command"
		self.TOPIC_LIGHT_LEVEL = f"jniHome/objects/sensor_{station_name}/events/lightLevel"
		self.TOPIC_MOTION = f"jniHome/objects/sensor_{station_name}/events/motion"
		self.TOPIC_TEMPERATURE = f"jniHome/objects/sensor_{station_name}/events/temperature"
		self.TOPIC_CO2 = f"jniHome/objects/sensor_{station_name}/events/co2"
		self.TOPIC_HUMIDITY = f"jniHome/objects/sensor_{station_name}/events/humidity"
		self.TOPIC_ALIVE_TICK = f"jniHome/services/sensor_{station_name}/aliveTick"
		
		self.state = self.INITIATING
		self.blocked = True
		self.connected = False
		self.keep_running = True
		self.mqtt_client: mqtt.MQTT | None = None
		self.first_connect = True
		self.ensure_mqtt_client()
	
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
	
	def on_message(self, client, userdata, message):
		topic = str(message.topic)
		command = message.payload.decode(self.UTF_8_NAME)
		if self.TOPIC_COMMAND == topic:
			if command == "exit":
				self.keep_running = False
				self.exit()

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
				self.mqtt_client.subscribe(self.TOPIC_COMMAND)
				print(f"Subscribed to '{self.TOPIC_COMMAND}'")
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

	def publish_temperature(self, temperature: float):
		if not self._self_check():
			print("MQTT not operational, not publishing temperature.")
			return
		try:
			now = datetime.now()
			javascript_date_string = now.isoformat()
			json_string = json.dumps({"temperature": temperature, "utcTime": javascript_date_string})

			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_TEMPERATURE, json_string)
		except Exception as e:
			error_message = f"Error publishing temperature to MQTT server: {e}"
			self._handle_error(error_message)

	def publish_co2(self, co2: int):
		if not self._self_check():
			print("MQTT not operational, not publishing CO2.")
			return
		try:
			now = datetime.now()
			javascript_date_string = now.isoformat()
			json_string = json.dumps({"co2": co2, "utcTime": javascript_date_string})

			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_CO2, json_string)
		except Exception as e:
			error_message = f"Error publishing CO2 to MQTT server: {e}"
			self._handle_error(error_message)

	def publish_light_level(self, light_level: float):
		if not self._self_check():
			print("MQTT not operational, not publishing light level.")
			return
		try:
			now = datetime.now()
			javascript_date_string = now.isoformat()

			json_string = json.dumps({"lightLevel": light_level, "utcTime": javascript_date_string})

			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_LIGHT_LEVEL, json_string)
		except Exception as e:
			error_message = f"Error publishing light level to MQTT server: {e}"
			self._handle_error(error_message)

	def publish_humidity(self, humidity: float):
		if not self._self_check():
			print("MQTT not operational, not publishing humidity.")
			return
		try:
			now = datetime.now()
			javascript_date_string = now.isoformat()

			json_string = json.dumps({"humidity": humidity, "utcTime": javascript_date_string})

			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_HUMIDITY, json_string)
		except Exception as e:
			error_message = f"Error publishing light level to MQTT server: {e}"
			self._handle_error(error_message)

	def publish_motion(self, motion_started: bool):
		if not self._self_check():
			print("MQTT not operational, not publishing motion.")
			return
		try:
			now = datetime.now()
			javascript_date_string = now.isoformat()

			json_string = json.dumps({"start": motion_started, "end": not motion_started, 
				"utcTime": javascript_date_string})

			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_MOTION, json_string)
		except Exception as e:
			error_message = f"Error publishing motion to MQTT server: {e}"
			self._handle_error(error_message)
	
	def publish_alive_tick(self):
		if not self._self_check():
			print("MQTT not operational, not publishing alive tick.")
			return
		try:
			self.ensure_mqtt_client()
			self.mqtt_client.publish(self.TOPIC_ALIVE_TICK, self.ALIVE_VALUE)
		except Exception as e:
			error_message = f"Error publishing alive tick to MQTT server: {e}"
			self._handle_error(error_message)
	
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
	
	def loop(self):
		if self.OPERATIONAL != self.state:
			print("MQTT not operational, not performing loop")
			return
		try:
			self.mqtt_client.loop()
		except Exception as e:
			# This is whether related to ESP32-S3, CircuitPython 8 or both...
			print(f"Ignoring an error while looping: {e}")


def main() -> None:
	print("Starting...")
	jni_wifi.connect_wifi()
	counter = 0
	bridge = MqttBridge("test_station")
	time_start = time.monotonic()
	seconds_keep_alive = 5
	print(f"Pushing an alive tick every 0.5 seconds for {seconds_keep_alive} seconds")
	while True:
		bridge.publish_alive_tick()
		counter += 1
		print(f"Published message #{counter}")
		time.sleep(0.5)
		# bridge.loop()  # Does not work with CP 8.0 Beta 2
		time_passed = time.monotonic() - time_start
		if time_passed > seconds_keep_alive:
			break
	bridge.exit()
	jni_wifi.disconnect_wifi()
	print("All done.")


if __name__ == "__main__":
	main()
