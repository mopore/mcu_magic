# Complete project details at https://RandomNerdTutorials.com
from umqttsimple import MQTTClient
import machine
import ubinascii

try:
    import usocket as socket
except:
    import socket

import time
import network

import esp
esp.osdebug(None)
print("System debug messages supressed.")

import gc
gc.collect()
print("GC performed.")

ssid = "MicroPython-AP"
password = "123456789"
print(f"Creating Access Point '{ssid}'")
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)
while ap.active() == False:
    pass
print("Access Point is up")
print(ap.ifconfig())

# Global variables for MQTT connection
mqtt_server = '192.168.4.2'
topic_sub = b'esp32/test'
topic_pub = b'esp32/test'
client_id = ubinascii.hexlify("esp32")
last_message = 0
message_interval = 2
counter = 0


def sub_cb(topic, msg):
    print(f"Message received: {(topic, msg)}")


def connect_and_subscribe():
    global client_id, mqtt_server, topic_sub
    client = MQTTClient(client_id=client_id, server=mqtt_server, keepalive=30)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client


try:
    print("Waiting for MQTT Server to connect to...")
    client = connect_and_subscribe()
except OSError as e:
    print(f"Error: {e}")

while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            print("Publishing new message")
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1
            if counter == 5:
                break
    except OSError as e:
        print(f"Error: {e}")
        break

print("Jobs are done.")
ap.active(False)
while ap.active():
    pass
print("Access Point deactiviated.")
print("Exit.")
