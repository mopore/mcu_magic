# https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test
# circup install adafruit_requests
# circup install adafruit_datetime
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


def translate_signal_strength(signal: int) -> int:
	"""Translate the signal strength from dBm to percentage."""
	if signal <= -100:
		return 0
	elif signal >= -50:
		return 100
	else:
		return 2 * (signal + 100)


def scan_wifis(verbose_scanning: bool = False) -> list[str]:
	print("Scanning wifis...") if verbose_scanning else None
	networks: list[wifi.Network] = []
	for network in wifi.radio.start_scanning_networks():
		networks.append(network)
	wifi.radio.stop_scanning_networks()
	networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
	ssids: list[str] = []
	for network in networks:
		print(f"SSID: {network.ssid}") if verbose_scanning else None
		ssids.append(network.ssid)
		#  print(f"BSSID: {network.bssid}")
		percentage = translate_signal_strength(network.rssi)
		print(f"Signal Strength: {percentage}%") if verbose_scanning else None
		print(f"Security: {network.authmode}\n") if verbose_scanning else None
	return ssids


def _connect_wifi(ssid: str, wifi_pwd: str) -> bool:
	connect_max_time = 20
	connected = False
	connect_start_time = time.monotonic()
	attempts_counter = 0
	while not connected and ((time.monotonic() - connect_start_time) < connect_max_time):
		try:
			wifi.radio.connect(ssid, wifi_pwd)	
			info = wifi.radio.ap_info
			print(f"Connected to {info.ssid}!")
			connected = True
		except ConnectionError:
			attempts_counter += 1
	return connected


def read_wifi_creds() -> list[tuple[str, str]]:
	print("Reading wifi credentials from secrets/jni_secrets.py...")
	try:
		# Old format did not have numbered SSIDs
		ssid = secrets["ssid"]
		password = secrets["password"]
		print(f"Found credentials in old format for: {ssid}")
		return [(ssid, password)]
	except KeyError:
		...

	# New format has numbered SSIDs
	credentials: list[tuple[str, str]] = []	
	counter = 0
	print("Looking for 'ssid_1' and 'wifi_password_1'...")
	while True:
		counter += 1
		try:
			ssid = secrets[f"ssid_{counter}"]
			password = secrets[f"wifi_password_{counter}"]
			print(f"Found credentials for: {ssid}")
			credentials.append((ssid, password))
		except KeyError:
			# No more SSIDs to try
			break
	if len(credentials) == 0:
		print("Could not find any credentials!")
		return []
	return credentials


def connect_wifi(
	sync_time=True 
) -> adafruit_requests.Session:
	http_session: adafruit_requests.Session | None = None
	if wifi.radio.ap_info is not None:
		print("Already connected!")
		pool = socketpool.SocketPool(wifi.radio)
		http_session = adafruit_requests.Session(pool, ssl.create_default_context())
		return http_session

	if wifi.radio.enabled is False:
		print("Enabling radio.")
		wifi.radio.enabled = True
	credentials = read_wifi_creds()
	multiple_creds = len(credentials) > 1
	connected = False
	if multiple_creds:
		scanned_ssids = scan_wifis()
		credentials_scanned_ssids = [c for c in credentials if c[0] in scanned_ssids]
		credentials_not_scanned = [c for c in credentials if c[0] not in scanned_ssids]
			
		# Try to connect to with credentials which SSID match the scanned SSIDs
		for ssid, wifi_pwd in credentials_scanned_ssids:
			print(f"Trying '{ssid}'...")
			connected = _connect_wifi(ssid, wifi_pwd)
			if connected:
				break
		if not connected:  # Try to connect with the rest of the credentials
			for ssid, wifi_pwd in credentials_not_scanned:
				print(f"Trying '{ssid}'...")
				connected = _connect_wifi(ssid, wifi_pwd)
				if connected:
					break
	else:  # Only one set of credentials
		ssid, wifi_pwd = credentials[0]
		connected = _connect_wifi(ssid, wifi_pwd)

	if connected is False:
		print("Could not connect to Wifi!")
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
	# Testing a second call of connect_wifi to see if returned session is useable.
	session = connect_wifi()
	TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
	text_to_show = session.get(TEXT_URL).text
	print(f"Text: {text_to_show}")
	disconnect_wifi()


if __name__ == "__main__":
	main()
