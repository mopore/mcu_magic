# See: https://learn.adafruit.com/adafruit-128x64-oled-featherwing?view=all#circuitpython
# Ensure to have "adafruit_displayio_sh1107" and "adafruit_display_text" installed
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text

import displayio
displayio.release_displays()

import terminalio
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


class BatteryOnOled:
    
    WIDTH = 128
    HEIGHT = 64
    WHITE = 0xFFFFFF

    def __init__(self, i2c) -> None:
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

        display = adafruit_displayio_sh1107.SH1107(
            display_bus, 
            width=self.WIDTH, 
            height=self.HEIGHT
        )
        splash = displayio.Group()
        display.show(splash)

        text = "Loading..." 
        battery_label = label.Label(terminalio.FONT, text=text, color=self.WHITE, x=0, y=30)
        splash.append(battery_label)
        self.battery_label = battery_label
        client_label = label.Label(terminalio.FONT, text=text, color=self.WHITE, x=0, y=30)
        splash.append(client_label)
        self.client_label = client_label

    def update_display(self, text: str) -> None:
        self.battery_label.text = get_power_info()
        new_x = int((self.WIDTH / 2) - (self.battery_label.width / 2))
        new_y = int(self.HEIGHT - 10) 
        self.battery_label.x = new_x
        self.battery_label.y = new_y 
        
        self.client_label.text = text
        new_x = int((self.WIDTH / 2) - (self.client_label.width / 2))
        new_y = int(10) 
        self.client_label.x = new_x
        self.client_label.y = new_y 
