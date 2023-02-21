import wifi

def translate_signal_strength(signel: int) -> int:
	"""Translate the signal strength from dBm to percentage."""
	if signel <= -100:
		return 0.0
	elif signel >= -50:
		return 100.0
	else:
		return 2 * (signel + 100)


def main() -> None:
	print("Scanning wifis...")
	networks: list[wifi.Network] = []
	for network in wifi.radio.start_scanning_networks():
		networks.append(network)
	wifi.radio.stop_scanning_networks()
	networks = sorted(networks, key=lambda net: net.rssi, reverse=True)
	for network in networks:
		print(f"SSID: {network.ssid}")
		#  print(f"BSSID: {network.bssid}")
		percentage = translate_signal_strength(network.rssi)
		print(f"Signal Strength: {percentage}%")
		#  print(f"Channel: {network.channel}")
		print(f"Security: {network.authmode}")
		print("")

if __name__ == "__main__":
	main()

