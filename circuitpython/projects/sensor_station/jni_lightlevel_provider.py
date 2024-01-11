# circup install adafruit_bh1750
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries

# SPDX-License-Identifier: Unlicense
import time
import board
import adafruit_bh1750


class LightlevelProvider:

    def __init__(self) -> None:
        self.baseline: None | float = None
        self.candidate: None | float = None
        
        #  i2c = board.I2C()
        i2c = board.STEMMA_I2C()  # type: ignore
        sensor = adafruit_bh1750.BH1750(i2c)
        self.sensor = sensor

    def get_lightlevel(self) -> float:
        current = self.sensor.lux
        
        if self.baseline is None:
            self.baseline = current
        else:
            if self.candidate is None:
                diff_candidate = abs(current - self.baseline)
                candidate_confirmed = diff_candidate > 0.1
                if candidate_confirmed:
                    self.candidate = current
            else:  # candidate is set
                diff_confirmation = abs(current - self.baseline)
                final_confirmation = diff_confirmation > 0.1
                if final_confirmation:
                    self.baseline = current
                self.candidate = None
        return self.baseline


def main() -> None:
    provider = LightlevelProvider()
    while True:
        result = provider.get_lightlevel()
        print(f"Light level: {result:.1f} Lumen")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
