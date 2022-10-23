# https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
# circup install adafruit_requests
import jni_wifi
import wifi
import socketpool
import ssl
import time
import rtc
import adafruit_requests
from adafruit_datetime import datetime
try:
	from secrets.jni_secrets import secrets
except ImportError:
	print("WiFi secrets are kept in secrets.py, please add them there!")
	raise


def main() -> None:
	print(f"The current time is {datetime.now().isoformat()}")
	jni_wifi.connect_wifi()
	pool = socketpool.SocketPool(wifi.radio)
	http_session = adafruit_requests.Session(pool, ssl.create_default_context())
	print("Requesting time from adafruit.io")
	aio_username = secrets["aio_username"]
	aio_key = secrets["aio_key"]
	location = "UTC"
	TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/struct?x-aio-key=%s&tz=%s" % (aio_username, aio_key, location)
	json_response = http_session.get(TIME_URL).json()
	jni_wifi.disconnect_wifi()
	print(f'Time is: {json_response}')
	#  year, mon, date, hour, min, sec, wday, yday, isdst
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
	print(f"The new current time is {datetime.now().isoformat()}")


if __name__ == "__main__":
	main()
