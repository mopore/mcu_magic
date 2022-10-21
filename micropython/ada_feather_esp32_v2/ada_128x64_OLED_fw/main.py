from machine import Pin, SoftI2C
import sh1107
from time import sleep


def display_hello(oled: sh1107.SH1107_I2C) -> None:
    oled.fill(0)
    for i in range(6):
        oled.text(f"Hello, World {i}!", 0, 3 + (i * 10))
    oled.show()


def display_text(oled: sh1107.SH1107_I2C, text: str) -> None:
    oled.fill(0)
    oled.text(text, 0, 0)
    oled.show()


def main() -> None:
    """ Sample code for the SH1107 OLED display with Sparkfun ESP32 Thing"""

    # print("Powering on NEOPIXEL_I2C_POWER pin...")
    # power_pin = Pin(2, Pin.OUT)
    # power_pin.value(1)

    print("Preparing I2C...")
    
    # NOTE: There is a bug with MicroPython on this port and the use of pin 22 for scl
    # As descibed in the documentation there is a bug with port 20 for as the I2C clock w/ MP
    i2c = SoftI2C(scl=Pin(14), sda=Pin(22))
    
    print("Preparing OLED w/ I2C...")
    oled_width = 128
    oled_height = 64
    oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c)

    print("Displaying hello...")
    display_hello(oled)

    print("Prepaing buttons...")
    # NOTE: The buttons must have an internal pull-up resistor to work!
    a_button = Pin(15, Pin.IN, Pin.PULL_UP)
    b_button = Pin(32, Pin.IN, Pin.PULL_UP)
    # NOTE: Needed to use pin 33 instead of Pin 14 since 14 is already used for I2C
    c_button = Pin(33, Pin.IN, Pin.PULL_UP)

    print("Waiting for button press...")
    while True:
        if a_button.value() == 0:
            print("Test A")
            display_text(oled, "A pressed")
        elif b_button.value() == 0:
            print("Test B")
            display_text(oled, "B pressed")
        elif c_button.value() == 0:
            print("Test C")
            display_text(oled, "C pressed")
        sleep(0.1)


if __name__ == "__main__":
    main()
