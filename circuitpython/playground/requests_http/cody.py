# https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
# circup install adafruit_requests
import jni_wifi
import wifi
import socketpool
import ssl
import adafruit_requests


def main() -> None:
	jni_wifi.connect_wifi()
	pool = socketpool.SocketPool(wifi.radio)
	http_session = adafruit_requests.Session(pool, ssl.create_default_context())
	print("Making an HTTP Get request to fetch some json")
	JSON_GET_URL = "https://httpbin.org/get"
	json_response = http_session.get(JSON_GET_URL).json()
	jni_wifi.disconnect_wifi()
	print(f'Retrieved JSON value for "origin": {json_response["origin"]}')


if __name__ == "__main__":
	main()
