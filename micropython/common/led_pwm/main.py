import machine
import utime

# Pin definitions
pwm_pin = machine.Pin(23, machine.Pin.OUT)

# Create a PWM object out of our pin object
pwm_led = machine.PWM(pwm_pin)


# Slowly fade LED brightness
while True:

    for i in range(1024):
        pwm_led.duty(i)
        utime.sleep_ms(2)
