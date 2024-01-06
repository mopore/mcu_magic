# circup install adafruit_bh1750
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries

# SPDX-License-Identifier: Unlicense
import time
import board
import adafruit_bh1750


class LightlevelProvider:

    def __init__(self) -> None:
        #  i2c = board.I2C()
        i2c = board.STEMMA_I2C()  # type: ignore
        sensor = adafruit_bh1750.BH1750(i2c)
        self.sensor = sensor

    def get_lightlevel(self) -> float:
        return self.sensor.lux


def main() -> None:
    provider = LightlevelProvider()
    while True:
        result = provider.get_lightlevel()
        print(f"Light level: {result:.1f} Lumen")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
