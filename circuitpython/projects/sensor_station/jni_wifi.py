import wifi
import time

try:
	from jni_secrets import secrets
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


def main() -> None:
	connect_wifi()
	print("Connected waiting 2 seconds before disconnect...")
	disconnect_wifi()


if __name__ == "__main__":
	main()
