# https://pypi.org/project/micropython-umqtt.robust/
# pip install micropython-umqtt.robust

#AWS MQTT client cert example for esp8266 or esp32 running MicroPython 1.9 
from umqtt.robust import MQTTClient
import time
import network

CERT_FILE = "/moisture_thing_1.cert.pem"
KEY_FILE = "/moisture_thing_1.private.key"

#if you change the ClientId make sure update AWS policy
MQTT_CLIENT_ID = "basicPubSub"
MQTT_PORT = 8883

#if you change the topic make sure update AWS policy
MQTT_TOPIC = "sdk/test/Python"

#Change the following three settings to match your environment
MQTT_HOST = "a6ygioa4gqbri-ats.iot.eu-central-1.amazonaws.com"
WIFI_SSID = "Loxodonta"
WIFI_PW = "?"

mqtt_client = None


def pub_msg(msg):
    global mqtt_client
    try:    
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise


def connect_mqtt():    
    global mqtt_client

    try:
        with open(KEY_FILE, "r") as f: 
            key = f.read()
        # print(f"Key: {key}")
            
        with open(CERT_FILE, "r") as f: 
            cert = f.read()
        # print(f"Cert: {cert}")

        mqtt_client = MQTTClient(
            client_id=MQTT_CLIENT_ID, 
            server=MQTT_HOST, 
            port=MQTT_PORT, 
            keepalive=5000, 
            ssl=True, 
            ssl_params={"cert": cert, "key": key, "server_side": False}
        )
        mqtt_client.connect()
        print('MQTT Connected')
        
    except Exception as e:
        print('Cannot connect MQTT: ' + str(e))
        raise


def do_wifi_connect() -> network.WLAN:
    wifi_client = network.WLAN(network.STA_IF)
    if not wifi_client.isconnected():
        print('connecting to Wifi...')
        wifi_client.active(True)
        wifi_client.connect(WIFI_SSID, WIFI_PW)
        wait_counter = 0
        while not wifi_client.isconnected():
            time.sleep(1)
            wait_counter += 1
            if wait_counter > 60:
                print("Giving up to wait for Wifi and will reset...")
                raise
    print('Connected to Wifi:', wifi_client.ifconfig())
    return wifi_client

        
#start execution
try:
    print("Connecting WIFI")
    do_wifi_connect()
    print("Connecting MQTT")
    connect_mqtt()
    print("Publishing")
    pub_msg("{\"AWS-MQTT-Sparkfun\":" + str(time.time()) + "}")
    print("OK")
    time.sleep(2)
    mqtt_client.disconnect()
    print("All done")
except Exception as e:
    print(str(e))
