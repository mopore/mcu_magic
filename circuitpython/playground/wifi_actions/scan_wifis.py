import wifi


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


def main() -> None:
	ssid_list = scan_wifis(verbose_scanning=False)
	print(f"Found {len(ssid_list)} SSIDs")


if __name__ == "__main__":
	main()
