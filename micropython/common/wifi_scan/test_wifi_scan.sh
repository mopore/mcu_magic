import esp
import network
import time

esp.osdebug(None)


print("Scanning for Wifis...")
wlan = network.WLAN(network.STA_IF)

wlan_active = wlan.active()
if wlan_active:
	print("WLAN already active.")
else:
	print("Activating WLAN")
	wlan.active(True)

print("Scanning...")
scan_result = wlan.scan()
print(f"Scan result...")
for row in scan_result:
	ssid = row[0].decode('utf-8')
	print(f"ssid: {ssid}")
	if ssid == "for-guests":
		print("Found guest wifi")

print("Deactivating WLAN")
wlan.active(False)
print("All done.")

