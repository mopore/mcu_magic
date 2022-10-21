import machine
import time
import utime

# Pin definitions
int_led = machine.Pin(5, machine.Pin.OUT)

LED_ON = 1
LED_OFF = 0
int_led.value(LED_OFF)

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Woke up from a deep sleep")
    for i in range(5):
        utime.sleep_ms(100)
        int_led.value(LED_ON)
        utime.sleep_ms(100)
        int_led.value(LED_OFF)
else:
    print("Regular start")
    int_led.value(LED_ON)
    time.sleep(3)
    int_led.value(LED_OFF)

time.sleep(2)
 
# put the device to sleep for 5 seconds
print("I feel tired...")
for i in range(2):
    utime.sleep_ms(200)
    int_led.value(LED_ON)
    utime.sleep_ms(200)
    int_led.value(LED_OFF)
machine.deepsleep(5000)
