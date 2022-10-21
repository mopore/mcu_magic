# Complete project details at https://RandomNerdTutorials.com

try:
  import usocket as socket
except:
  import socket

import time
import network

import esp
esp.osdebug(None)

import gc
gc.collect()


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect("Equus", "Gradation%Lustiness%Brisket%Trimness%Singer3")
        while not sta_if.isconnected():
            time.sleep(1)
            pass
    print('Connected to network config:', sta_if.ifconfig())

do_connect()

def web_page():
  html = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
  <body><h1>Hello, World!</h1></body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

conn, addr = s.accept()
print('Got a connection from %s' % str(addr))
request = conn.recv(1024)
print('Content = %s' % str(request))
response = web_page()
conn.send(response)
conn.close()
