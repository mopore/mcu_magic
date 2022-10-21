import wifi
import socketpool
import time
import adafruit_minimqtt.adafruit_minimqtt as mqtt

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def connect_wifi() -> None:
    connect_max_secs = 10
    connected = False
    ip_address = wifi.radio.ipv4_address
    if ip_address is not None:
        print("Already connected.")
        return
    connect_start_time = time.monotonic()
    attempts_counter = 0
    while not connected and ((time.monotonic() - connect_start_time) < connect_max_secs):
        try:
            print("Connecting to WiFi...")
            if wifi.radio.enabled:
                print("Deactivating already active Wifi first...")
                wifi.radio.enabled = False
                time.sleep(2)
            wifi.radio.enabled = True
            ssid = secrets['ssid']
            wifi_pwd = secrets['password']
            print(f"Tyring to connect to {ssid}")
            wifi.radio.connect(ssid, wifi_pwd)	
            ip_address = wifi.radio.ipv4_address
            print(f"Having IP: {ip_address}")
            connected = True 
        except ConnectionError as e:
            print(f"Error: {e}")
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

    ACCEPTABLE_ERROR_SECS = 5

    def __init__(self) -> None:
        pool = socketpool.SocketPool(wifi.radio)
        mqtt_server = secrets['mqtt_server']
        client_id = f"client_{time.time()}"
        print(f"Client ID: {client_id}")
        mqtt_client = mqtt.MQTT(
            client_id=client_id,
            broker=mqtt_server, 
            socket_pool=pool, 
            is_ssl=False
        )
        mqtt_client.on_message = self.on_message
        self.mqtt_client = mqtt_client
        self.last_error_time: float | None = None

    def connect(self):
        self.mqtt_client.connect()
        self.message_received = False

    def on_message(self, client, topic, message):
        print("New message on topic {0}: {1}".format(topic, message))
        self.message_received = True

    def subscribe(self, topic):
        print("Subscribing to topice...")
        self.mqtt_client.subscribe(topic)

    def publish(self, topic, message):
        try:
            self.mqtt_client.publish(topic, message)
            self.last_error_time = None
        except Exception:
            if self.last_error_time is not None:
                error_diff_time = time.monotonic() - self.last_error_time
                if error_diff_time > self.ACCEPTABLE_ERROR_SECS:
                    raise Exception("Too many errors publishing.") 
            else:
                self.last_error_time = time.monotonic()

    def disconnect(self):
        print("Disconnecting from MQTT")
        self.mqtt_client.disconnect()