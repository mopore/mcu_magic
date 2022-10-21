import network
import time

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py!")
    raise


# Change this to install a different library

# LIBRARY_TO_INSTALL = "sh1107-micropython"
LIBRARY_TO_INSTALL = "micropython-iotc"  # IoT center from Microsoft
#  LIBRARY_TO_INSTALL = "itertools"
# Available libraries: https://github.com/mcauser/awesome-micropython
def do_wifi_connect() -> network.WLAN:
    import network
    wifi_client = network.WLAN(network.STA_IF)
    if not wifi_client.isconnected():
        print('connecting to Wifi...')
        wifi_client.active(True)
        wifi_client.connect(secrets["ssid"], secrets["password"])
        while not wifi_client.isconnected():
            time.sleep(1)
            pass
    print('Connected to Wifi:', wifi_client.ifconfig())
    return wifi_client


def main() -> None:
    print(f"This will install the library {LIBRARY_TO_INSTALL}")
    
    print("Opening wifi...")
    wifi_client = do_wifi_connect()

    try:
        import upip
        print("Installing library...")
        upip.install(LIBRARY_TO_INSTALL)
        print("Library installed!")
    except Exception as e:
        print("Error installing library:", e)

    print("Disconnecting from Wifi...")
    wifi_client.disconnect()
    wifi_client.active(False)
                

if __name__ == "__main__":
    main()
