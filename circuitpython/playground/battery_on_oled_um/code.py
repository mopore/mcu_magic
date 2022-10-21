# See: https://learn.adafruit.com/adafruit-128x64-oled-featherwing?view=all#circuitpython
# Ensure to have "adafruit_displayio_sh1107" and "adafruit_display_text" installed
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text

import board
import displayio
import terminalio
import time
import feathers3

# can try import bitmap_label below for alternative
from adafruit_display_text import label
import adafruit_displayio_sh1107


def get_power_info() -> str: 
    on_usbc_power = feathers3.get_vbus_present()
    if on_usbc_power:
        return "USB-C connected."
    else:
        battery_voltage = feathers3.get_battery_voltage()
        return f"Battery: {battery_voltage:.1f}V" 


def main() -> None:
    displayio.release_displays()
    # Use for I2C
    i2c = board.I2C()
    display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

    WIDTH = 128
    HEIGHT = 64
    WHITE = 0xFFFFFF

    display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
    splash = displayio.Group()
    display.show(splash)

    text = "Loading..." 
    text_label = label.Label(terminalio.FONT, text=text, color=WHITE, x=0, y=30)
    splash.append(text_label)

    while True:
        text_label.text = get_power_info()
        new_x = int((WIDTH / 2) - (text_label.width / 2))
        new_y = int(HEIGHT / 2) 
        text_label.x = new_x
        text_label.y = new_y 
        time.sleep(1)


if __name__ == "__main__":
    main()