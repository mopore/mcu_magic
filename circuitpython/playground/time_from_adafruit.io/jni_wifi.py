# https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
# circup install adafruit_requests
import wifi
import time
import socketpool
import ssl
import rtc
import adafruit_requests
from adafruit_datetime import datetime

try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


def connect_wifi(sync_time=True) -> adafruit_requests.Session:
	http_session: adafruit_requests.Session | None = None
	if wifi.radio.ap_info is not None:
		print("Already connected!")
		pool = socketpool.SocketPool(wifi.radio)
		http_session = adafruit_requests.Session(pool, ssl.create_default_context())
		return http_session

	connect_max_time = 30
	connected = False
	connect_start_time = time.monotonic()
	attempts_counter = 0
	if wifi.radio.enabled is False:
		print("Enabeling radio.")
		wifi.radio.enabled = True
	while not connected and ((time.monotonic() - connect_start_time) < connect_max_time):
		try:
			ssid = secrets['ssid']
			wifi_pwd = secrets['password']
			print("Connecting to WiFi...")
			wifi.radio.connect(ssid, wifi_pwd)	
			info = wifi.radio.ap_info
			print(f"Connected to {info.ssid}!")
			connected = True
		except ConnectionError as e:
			attempts_counter += 1
	if connected is False:
		print(f"Could not connect to Wifi afer {attempts_counter} attempts!")
		wifi.radio.enabled = False
		raise ConnectionError()
	pool = socketpool.SocketPool(wifi.radio)
	http_session = adafruit_requests.Session(pool, ssl.create_default_context())

	if sync_time is True:
		try:
			print("Connecting to time server...")
			aio_username = secrets["aio_username"]
			aio_key = secrets["aio_key"]
			location = "UTC"
			TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/struct?x-aio-key=%s&tz=%s" % (aio_username, aio_key, location)
			json_response = http_session.get(TIME_URL).json()
			t = time.struct_time(
				(
					json_response["year"],
					json_response["mon"],
					json_response["mday"],
					json_response["hour"],
					json_response["min"],
					json_response["sec"],
					json_response["wday"],
					-1,
					-1,
				)
			)
			r = rtc.RTC()
			r.datetime = t
			print("Time synced.")
		except Exception as e:
			print(f"Error syncing time from adafruit.io: {e}")
	return http_session


def disconnect_wifi() -> None:
	print("Disconnecting from WiFi...")
	wifi.radio.enabled = False
	print("Disconnected from WiFi!")


def main() -> None:
	print(f"The current time is {datetime.now().isoformat()}")
	connect_wifi()
	print(f"The new current time is {datetime.now().isoformat()}")
	session = connect_wifi()
	TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
	text_to_show = session.get(TEXT_URL).text
	print(f"Text: {text_to_show}")
	disconnect_wifi()


if __name__ == "__main__":
	main()
