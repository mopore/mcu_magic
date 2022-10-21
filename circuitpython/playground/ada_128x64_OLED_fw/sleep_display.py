# See: https://learn.adafruit.com/adafruit-128x64-oled-featherwing?view=all#circuitpython
# Ensure to have "adafruit_displayio_sh1107" and "adafruit_display_tex" installed
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text

import board
import displayio
import terminalio
import asyncio
import time
from adafruit_display_text import label
import adafruit_displayio_sh1107
# from adafruit_lc709203f import LC709203F

from digitalio import DigitalInOut, Pull


class ButtonListener:
    def __init__(self, click_callback) -> None:
        self.click_callback = click_callback
        button_a = DigitalInOut(board.D9)
        button_a.switch_to_input(pull=Pull.UP)
        self.button_a = button_a
        asyncio.create_task(self.run())
        
    async def run(self):
        while True:
            if not self.button_a.value:
                self.click_callback()
            await asyncio.sleep(0.1)


class OledManager:
    
    TIME_BEFORE_SLEEP = 5
    
    def __init__(self) -> None:
        asyncio.create_task(self.run())
        
    async def run(self):
        self.last_show = time.time()
        self.showing = True        

        displayio.release_displays()
        i2c = board.I2C()
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

        WIDTH = 128
        HEIGHT = 64
        WHITE = 0xFFFFFF

        display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
        splash = displayio.Group()
        display.show(splash)
        self.display = display

        self.text = "Hit 'A' to wake."
        text_label = label.Label(terminalio.FONT, text=self.text, color=WHITE, x=0, y=30)
        splash.append(text_label)

        while True:
            if self.showing:
                now = time.time()
                time_passed = now - self.last_show
                if time_passed > self.TIME_BEFORE_SLEEP:
                    self.sleep()
                else:
                    text_label.text = self.text
                    new_x = int((WIDTH / 2) - (text_label.width / 2))
                    new_y = int(HEIGHT / 2) 
                    text_label.x = new_x
                    text_label.y = new_y 
            await asyncio.sleep(0.1)

    def sleep(self) -> None:
        self.showing = False
        self.display.sleep()

    def wake(self) -> None:
        self.showing = True
        self.last_show = time.time()
        self.display.wake()


async def main():
    oled_manager = OledManager()
    text = ""

    def click_callback():
        if not oled_manager.showing:
            oled_manager.wake()

    button_listener = ButtonListener(click_callback) 
    counter = 0
    while True:
        counter += 1
        oled_manager.text = f"counter: {counter}"
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
