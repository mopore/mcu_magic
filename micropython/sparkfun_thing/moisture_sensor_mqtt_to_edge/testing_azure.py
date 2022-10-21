from machine import SoftI2C, Pin, deepsleep, reset
import time
import network
import random
from umqtt.simple import MQTTClient
import ubinascii
from stemma_soil_sensor import StemmaSoilSensor

# AZURE_MEASUREMENT_NAME = "moisture2"
SLEEP_1H = 3_600_000
SLEEP_5MIN = 300_000
AZURE_MEASUREMENT_NAME = "testMoisture"
LED_ON = 1
LED_OFF = 0
internal_led = Pin(5, Pin.OUT)
mqtt_message_published = False

try:
    from secrets import secrets
except ImportError:
    print("WiFi and Azure secrets are kept in secrets.py!")
    raise


def blink_hello() -> None:
    for _ in range(5):
        internal_led.value(LED_ON)
        time.sleep(0.2)
        internal_led.value(LED_OFF)
        time.sleep(0.2) 


def blink_connecting() -> None:
    for _ in range(2):
        internal_led.value(LED_ON)
        time.sleep(0.1)
        internal_led.value(LED_OFF)
        time.sleep(0.1) 
    

def do_wifi_connect() -> network.WLAN:
    wifi_client = network.WLAN(network.STA_IF)
    if not wifi_client.isconnected():
        print('connecting to Wifi...')
        wifi_client.active(True)
        wifi_client.connect(secrets["ssid"], secrets["password"])
        wait_counter = 0
        while not wifi_client.isconnected():
            time.sleep(1)
            blink_connecting()
            wait_counter += 1
            if wait_counter > 60:
                print("Giving up to wait for Wifi and will reset...")
                reset()
    print('Connected to Wifi:', wifi_client.ifconfig())
    return wifi_client


def publish_to_azure(raw_value: float) -> None:
    import iotc

    id_scope = secrets["id_scope"]
    device_id = secrets["device_id"]
    device_key = secrets["device_primary_key"]  # or use device key directly

    conn_type: iotc.IoTCConnectType = iotc.IoTCConnectType.DEVICE_KEY
    azure_client = iotc.IoTCClient(id_scope, device_id, conn_type, device_key)

    print("Connecting to Azure Iot Central...")
    azure_client.connect()
    # raise Exception("Test Error")
    print("Connected to Azure Iot Central")
    print(f"Publishing value: {raw_value}")
    azure_client.send_telemetry({f"{AZURE_MEASUREMENT_NAME}": raw_value})
    print("Value published")
    print("Waiting 3 seconds...")
    time.sleep(3)


def publish_to_mqtt(raw_value: float, azureErrorMessage: str | None) -> None:
    topic = b"jniHome/objects/moisture_sensor_1/events/moisture"
    error_topic = b"jniHome/objects/moisture_sensor_1/events/moisture_error"
    id_random = random.randrange(1000)
    client_id = ubinascii.hexlify(f"moisture_sensor_{id_random}")
    server_ip = "192.168.199.119"
    mqtt_client = MQTTClient(
        client_id=client_id, 
        server=server_ip, 
        keepalive=30)

    def check_message_cb(topic, msg):
        global mqtt_message_published
        mqtt_message_published = True
        print("Message is on server.")

    mqtt_client.set_callback(check_message_cb)
    print("Connecting to MQTT server...")
    mqtt_client.connect()
    # raise Exception("Test Error")
    print(f"Connected to MQTT server at {server_ip}")
    if azureErrorMessage is not None:
        mqtt_client.subscribe(error_topic)
        mqtt_client.publish(error_topic, azureErrorMessage)
        print(f"Published error message: {azureErrorMessage}")
    else:
        mqtt_client.subscribe(topic)
        mqtt_client.publish(topic, str(raw_value))
        print(f"Published raw value: {raw_value}")

    counter = 0
    print("Checking for message...")
    while not mqtt_message_published:
        mqtt_client.check_msg()
        time.sleep(0.5)
        counter += 1
        if counter == 60:
            print("Message not sent!")
            break

    print("Disconnecting from MQTT server...")
    mqtt_client.disconnect()
    print("Disconnected from MQTT server")


def main() -> None:
    print("Starting...")
    blink_hello()

    # TODO Make the measurement...
    internal_led.value(LED_ON)
    avg_value = 2.2
    print(f"Averaged value: {avg_value}")
    internal_led.value(LED_OFF)

    print("Opening wifi...")
    wifi_client = do_wifi_connect()

    print("Going into sending mode...")
    internal_led.value(LED_ON)
    azureErrorMessage: None | str = None
    try: 
        print("Publishing averaged value to Azure...")
        publish_to_azure(avg_value)
    except Exception as e:
        azureErrorMessage = f"Error publishing to azure: {e}"
        print(azureErrorMessage)
    
    mqttErrorMessage: None | str = None
    try:
        print("Publishing averaged value to MQTT...")
        publish_to_mqtt(avg_value, azureErrorMessage)
    except Exception as e:
        mqttErrorMessage = f"Error publishing to MQTT: {e}"
        print(mqttErrorMessage)
 
    print("Disconnecting from Wifi...")
    wifi_client.disconnect()
    wifi_client.active(False)

    print("Going into inactivity mode...")
    internal_led.value(LED_OFF)

    seconds_counter = 0
    # Blink internal led every 5 seconds to signify all is done.
    # Go into deep sleep for an hour after 60 seconds of inactivity.
    while True:
        internal_led.value(0)
        time.sleep(5)
        seconds_counter += 5
        internal_led.value(1)
        time.sleep(1)
        seconds_counter += 1
        deepsleep_after_minute = seconds_counter > 60
        if deepsleep_after_minute:
            print("Going into deep sleep...")
            deepsleep_time = SLEEP_1H
            if azureErrorMessage is not None:
                deepsleep_time = SLEEP_5MIN
            deepsleep(deepsleep_time)
                

if __name__ == "__main__":
    main()
