# See: https://learn.adafruit.com/joy-featherwing/circuit-python-wiring-test
# circup install adafruit_seesaw
import time
import board
from micropython import const
from adafruit_seesaw.seesaw import Seesaw

i2c_bus = board.I2C()
ss = Seesaw(i2c_bus)

BUTTON_RIGHT = const(6)
BUTTON_DOWN = const(7)
BUTTON_LEFT = const(9)
BUTTON_UP = const(10)
BUTTON_SEL = const(14)
button_mask = const(
    (1 << BUTTON_RIGHT)
    | (1 << BUTTON_DOWN)
    | (1 << BUTTON_LEFT)
    | (1 << BUTTON_UP)
    | (1 << BUTTON_SEL)
)
STICK_X = const(3)
STICK_Y = const(2)

ss.pin_mode_bulk(button_mask, ss.INPUT_PULLUP)


class Calibration:
    def __init__(self, start_x: int, start_y: int):
        self.start_x = start_x
        self.start_y = start_y
        self.x = start_x
        self.y = start_y
        self.x_min = start_x
        self.x_max = start_x
        self.y_min = start_y
        self.y_max = start_y

    def update(self, x: int, y: int):
        if (abs(x - self.x) > 3) or (abs(y - self.y) > 3):
            if x < self.x_min:
                self.x_min = x
            if x > self.x_max:
                self.x_max = x
            if y < self.y_min:
                self.y_min = y
            if y > self.y_max:
                self.y_max = y
            self.x = x
            self.y = y

    def _percentage_to_extreme(self, actual: int, start: int, min: int, max: int) -> int:
        perc_extreme = 0
        if actual < start:
            range = start - min
            share_abs = start - actual
            if range > 0:
                share_rel = (share_abs / range) * 100
                perc_extreme = share_rel * -1 
        else:
            range = max - start
            share_abs = actual - start
            if range > 0:
                perc_extreme = (share_abs / range) * 100
        return int(perc_extreme) 

    def print(self):
        x_rel = self._percentage_to_extreme(self.x, self.start_x, self.x_min, self.x_max)
        y_rel = self._percentage_to_extreme(self.y, self.start_y, self.y_min, self.y_max) * -1
        print(f"X: {x_rel}\t\tY: {y_rel}")


print("Please move stick or press button.")
start_x = ss.analog_read(STICK_X)
start_y = ss.analog_read(STICK_Y)
calib = Calibration(start_x, start_y)

while True:
    x = ss.analog_read(STICK_X)
    y = ss.analog_read(STICK_Y)
    calib.update(x, y)
    calib.print()

    buttons = ss.digital_read_bulk(button_mask)
    if not buttons & (1 << BUTTON_RIGHT):
        print("Button A pressed")

    if not buttons & (1 << BUTTON_DOWN):
        print("Button B pressed")

    if not buttons & (1 << BUTTON_LEFT):
        print("Button Y pressed")

    if not buttons & (1 << BUTTON_UP):
        print("Button x pressed")

    if not buttons & (1 << BUTTON_SEL):
        print("Button SEL pressed")

    time.sleep(0.1)
