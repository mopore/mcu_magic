# https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
# circup install adafruit_requests
import jni_wifi
from adafruit_datetime import datetime


def main() -> None:
	print(f"The current time is {datetime.now().isoformat()}")
	jni_wifi.connect_wifi()
	print(f"The new current time is {datetime.now().isoformat()}")
	session = jni_wifi.connect_wifi()
	TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
	text_to_show = session.get(TEXT_URL).text
	print(f"Text: {text_to_show}")
	jni_wifi.disconnect_wifi()


if __name__ == "__main__":
	main()
