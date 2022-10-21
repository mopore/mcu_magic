import machine
import sys
import utime

# Pin definitions
repl_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
repl_led = machine.Pin(5, machine.Pin.OUT)
ext_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
pwm_pin = machine.Pin(27, machine.Pin.OUT)

# Create a PWM object out of our pin object
pwm = machine.PWM(pwm_pin)

int_led_state_on = False
ON_STATE = 1
OFF_STATE = 0

# Slowly fade LED brightness
while True:

    # If button 0 is pressed, switch interal LED
    if repl_button.value() == 0:
        int_led_state_on = not int_led_state_on
        if int_led_state_on:
            repl_led.value(ON_STATE)
        else:
            repl_led.value(OFF_STATE)



    # Increase brightness of LED if ext_button is held
    for i in range(1024):
        if ext_button.value() == 0:
            pwm.duty(i)
            utime.sleep_ms(2)
        else:
            pwm.duty(OFF_STATE)
