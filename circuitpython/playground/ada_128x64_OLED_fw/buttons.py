# See: https://learn.adafruit.com/adafruit-128x64-oled-featherwing?view=all#circuitpython
# Ensure to have "adafruit_displayio_sh1107" and "adafruit_display_tex" installed
# circup install adafruit_displayio_sh1107
# circup install adafruit_display_text
import board
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1107
from digitalio import DigitalInOut, Pull

# Preparing A,B,C buttons on FeatherWing
button_a = DigitalInOut(board.D9)
button_a.switch_to_input(pull=Pull.UP)
button_b = DigitalInOut(board.D6)
button_b.switch_to_input(pull=Pull.UP)
button_c = DigitalInOut(board.D5)
button_c.switch_to_input(pull=Pull.UP)

displayio.release_displays()
# Use for I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

WIDTH = 128
HEIGHT = 64
WHITE = 0xFFFFFF
DEFAULT_TEXT = "Press A,B or C..."


display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
splash = displayio.Group()
display.show(splash)

text_label = label.Label(terminalio.FONT, text=DEFAULT_TEXT, color=WHITE, x=0, y=30)
splash.append(text_label)
button_down = False


def change_text_label(new_text: str) -> None:
    print(f"Changing text to {new_text}")
    text_label.text = new_text
    new_x = int((WIDTH / 2) - (text_label.width / 2))
    new_y = int(HEIGHT / 2) 
    text_label.x = new_x
    text_label.y = new_y 


while True:
    if not button_down:
        if not button_a.value:
            change_text_label("'A' pressed")
            button_down = True
        elif not button_b.value:
            change_text_label("'B' pressed")
            button_down = True
        elif not button_c.value:
            change_text_label("'C' pressed")
            button_down = True
    else:
        if button_a.value and button_b.value and button_c.value:
            change_text_label("Button released")
            button_down = False

