# See: https://learn.adafruit.com/joy-featherwing/circuit-python-wiring-test
# circup install adafruit_seesaw
import time
import board
from adafruit_seesaw.seesaw import Seesaw


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
        self.x_rel = 0
        self.y_rel = 0

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
            self.x_rel = self._percentage_to_extreme(self.x, self.start_x, self.x_min, self.x_max)
            self.y_rel = self._percentage_to_extreme(self.y, self.start_y, self.y_min, self.y_max) * -1

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
        print(f"X: {self.x_rel}\t\tY: {self.y_rel}")


class JoyFw():
    
    def __init__(self) -> None:
        i2c_bus = board.I2C()
        ss = Seesaw(i2c_bus)

        self.BUTTON_RIGHT = 6
        self.BUTTON_DOWN = 7
        self.BUTTON_LEFT = 9
        self.BUTTON_UP = 10
        self.BUTTON_SEL = 14
        self.BUTTON_MASK = (
            (1 << self.BUTTON_RIGHT) | 
            (1 << self.BUTTON_DOWN) | 
            (1 << self.BUTTON_LEFT) | 
            (1 << self.BUTTON_UP) | 
            (1 << self.BUTTON_SEL)
        )
        self.STICK_X = 3
        self.STICK_Y = 2
        ss.pin_mode_bulk(self.BUTTON_MASK, ss.INPUT_PULLUP)
        self.ss = ss
        start_x = ss.analog_read(self.STICK_X)
        start_y = ss.analog_read(self.STICK_Y)
        self.calib = Calibration(start_x, start_y)
        self.button_down = False
    
    def tick(self) -> None:
        x = self.ss.analog_read(self.STICK_X)
        y = self.ss.analog_read(self.STICK_Y)
        self.calib.update(x, y)
        self.calib.print()

        buttons = self.ss.digital_read_bulk(self.BUTTON_MASK)
        if not self.button_down:
            if not buttons & (1 << self.BUTTON_RIGHT):
                print("Button A pressed")
                self.button_down = True

            if not buttons & (1 << self.BUTTON_DOWN):
                print("Button B pressed")
                self.button_down = True

            if not buttons & (1 << self.BUTTON_LEFT):
                print("Button Y pressed")
                self.button_down = True

            if not buttons & (1 << self.BUTTON_UP):
                print("Button x pressed")
                self.button_down = True

            if not buttons & (1 << self.BUTTON_SEL):
                print("Button SEL pressed")
                self.button_down = True
        else:
            if (
                buttons & (1 << self.BUTTON_RIGHT) and 
                buttons & (1 << self.BUTTON_DOWN) and 
                buttons & (1 << self.BUTTON_LEFT) and 
                buttons & (1 << self.BUTTON_UP) and 
                buttons & (1 << self.BUTTON_SEL)
            ):
                self.button_down = False


def main() -> None:
    wing = JoyFw()
    print("Please move stick or press button.")

    while True:
        wing.tick()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
