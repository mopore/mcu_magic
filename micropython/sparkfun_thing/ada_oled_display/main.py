from machine import Pin, SoftI2C
import sh1107
from time import sleep


def display_hello(oled: SH1107.SH1107_I2C) -> None:
    oled.fill(0)
    for i in range(6):
        oled.text(f"Hello, World {i}!", 0, 3 + (i * 10))
    oled.show()


def display_text(oled: SH1107.SH1107_I2C, text: str) -> None:
    oled.fill(0)
    oled.text(text, 0, 0)
    oled.show()


def main() -> None:
    """ Sample code for the SH1107 OLED display with Sparkfun ESP32 Thing"""

    print("Preparing I2C...")
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

    print("Preparing OLED w/ I2C...")
    oled_width = 128
    oled_height = 64
    oled = sh1107.SH1107_I2C(oled_width, oled_height, i2c)

    print("Displaying hello...")
    display_hello(oled)

    print("Prepaing buttons...")
    # NOTE: The buttons must have an internal pull-up resistor to work!
    a_button = Pin(18, Pin.IN, Pin.PULL_UP)
    b_button = Pin(23, Pin.IN, Pin.PULL_UP)
    c_button = Pin(19, Pin.IN, Pin.PULL_UP)

    print("Waiting for button press...")
    while True:
        if a_button.value() == 0:
            display_text(oled, "A pressed")
        elif b_button.value() == 0:
            display_text(oled, "B pressed")
        elif c_button.value() == 0:
            display_text(oled, "C pressed")
        sleep(0.1)


if __name__ == "__main__":
    main()
