import machine
import time

# Put an led on the marked Pin 13
ext_led = machine.Pin(13, machine.Pin.OUT)

ON_STATE = 1
OFF_STATE = 0

print("Starting external LED simple...")
while True:
    ext_led.value(ON_STATE)
    time.sleep(1)
    ext_led.value(OFF_STATE)
    time.sleep(1)
