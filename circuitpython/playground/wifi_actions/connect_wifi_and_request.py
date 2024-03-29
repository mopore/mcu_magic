# circup install adafruit_requests
import wifi
import socketpool
import ssl
import time

import adafruit_requests


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
			# JNI's personal Wifi hotspot
			ssid = 'PD-jni-iphone-22'
			password = '4axw57v41k1pf'
			wifi.radio.connect(ssid, password)	
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
	url = "http://httpbin.org/get"
	print(f"Sending get to {url}")
	pool = socketpool.SocketPool(wifi.radio)
	session = adafruit_requests.Session(pool, ssl.create_default_context())
	response = session.get(url)
	json_text = response.json()
	response.close()
	print("Response is: ", json_text)
	disconnect_wifi()


if __name__ == "__main__":
	main()

