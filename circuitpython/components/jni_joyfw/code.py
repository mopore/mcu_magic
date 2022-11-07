# See: https://learn.adafruit.com/joy-featherwing/circuit-python-wiring-test
# circup install adafruit_seesaw
import time
import board
import os
from adafruit_seesaw.seesaw import Seesaw


class JniJoyFwListener():
    
    def on_move(self, x: int, y: int) -> None:
        ...
    
    def on_button_a(self) -> None:
        ...

    def on_button_b(self) -> None:
        ...

    def on_button_x(self) -> None:
        ...

    def on_button_y(self) -> None:
        ...

    def on_button_sel(self) -> None:
        ...


class Calibration(JniJoyFwListener):

    DEADZONE_PERCENT = 20
    
    def __init__(
        self, 
        start_x: int, 
        start_y: int,
        x_min: int | None = None,
        y_min: int | None = None,
        x_max: int | None = None,
        y_max: int | None = None, 
    ):
        self.start_x = start_x
        self.start_y = start_y
        self.x_min = start_x

        if x_min is not None:
            self.x_min = x_min
        self.y_min = start_y
        if y_min is not None:
            self.y_min = y_min
        self.x_max = start_x
        if x_max is not None:
            self.x_max = x_max
        self.y_max = start_y
        if y_max is not None:
            self.y_max = y_max

        self.x = start_x
        self.y = start_y
        self.x_rel = 0
        self.y_rel = 0
        self.calib_mode = False

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
        print(f"\tX: {self.x_rel}        \tY: {self.y_rel}    ", end="\r")

    def on_button_a(self) -> None:
        print(f"Current calibration: {self.x_min}, {self.x_max}, {self.y_min}, {self.y_max}")
        self.calib_mode = False

        
class JniJoyFw():

    CALIB_FILEPATH = "joy_fw_calibration.txt"
    
    def __init__(self) -> None:
        i2c_bus = board.I2C()
        ss = Seesaw(i2c_bus)

        self.BUTTON_A = 6
        self.BUTTON_B = 7
        self.BUTTON_Y = 9
        self.BUTTON_X = 10
        self.BUTTON_SEL = 14
        self.BUTTON_MASK = (
            (1 << self.BUTTON_A) | 
            (1 << self.BUTTON_B) | 
            (1 << self.BUTTON_Y) | 
            (1 << self.BUTTON_X) | 
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
        self.listener: None | JniJoyFwListener = None
    
    def set_listener(self, listener: None | JniJoyFwListener) -> None:
        self.listener = listener

    def needs_calibration(self) -> bool:
        # TODO Determine if calibration is needed.
        root_content = os.listdir("/")
        if self.CALIB_FILEPATH in root_content: 
            print(f"{self.CALIB_FILEPATH} is in {root_content}")
            return False
        else:
            return True
    
    def calibrate(self) -> None:
        print("Calibration: Move stick in all dimensions and press 'A'...")
        self.listener = self.calib
        self.calib.calib_mode = True
        while self.calib.calib_mode:
            self.tick()
    
    def tick(self) -> None:
        x = self.ss.analog_read(self.STICK_X)
        y = self.ss.analog_read(self.STICK_Y)
        self.calib.update(x, y)
        if self.calib.calib_mode:
            self.calib.print()
        else:  # Normal mode
            if (
                abs(self.calib.x_rel) > Calibration.DEADZONE_PERCENT or
                abs(self.calib.y_rel) > Calibration.DEADZONE_PERCENT
            ):
                self.listener.on_move(self.calib.x_rel, self.calib.y_rel)

        buttons = self.ss.digital_read_bulk(self.BUTTON_MASK)
        if not self.button_down:
            if not buttons & (1 << self.BUTTON_A):
                if self.listener is not None:
                    self.listener.on_button_a()
                self.button_down = True

            if not buttons & (1 << self.BUTTON_B):
                if self.listener is not None:
                    self.listener.on_button_b()
                self.button_down = True

            if not buttons & (1 << self.BUTTON_Y):
                if self.listener is not None:
                    self.listener.on_button_y()
                self.button_down = True

            if not buttons & (1 << self.BUTTON_X):
                if self.listener is not None:
                    self.listener.on_button_x()
                self.button_down = True

            if not buttons & (1 << self.BUTTON_SEL):
                if self.listener is not None:
                    self.listener.on_button_sel()
                self.button_down = True
        else:
            if (
                buttons & (1 << self.BUTTON_A) and 
                buttons & (1 << self.BUTTON_B) and 
                buttons & (1 << self.BUTTON_Y) and 
                buttons & (1 << self.BUTTON_X) and 
                buttons & (1 << self.BUTTON_SEL)
            ):
                self.button_down = False


class NormalListener(JniJoyFwListener):
    
    def on_button_a(self) -> None:
        print("Button A!")
    
    def on_move(self, x: int, y: int) -> None:
        print(f"x: {x}, y: {y}")


def main() -> None:
    wing = JniJoyFw()
    if wing.needs_calibration():
        wing.calibrate()
        print("Calibrated.")
    print("Normal mode...")
    wing.set_listener(NormalListener())
    while True:
        wing.tick()
        # time.sleep(0.1)


if __name__ == "__main__":
    main()
