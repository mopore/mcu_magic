# circup install adafruit_scd4x

import time
import board
import adafruit_scd4x


class Airquality:

    def __init__(self, co2: int, temperature: float, humidity: float) -> None:
        self.co2 = co2
        self.temperature = temperature
        self.humidity = humidity


class AirqualityProvider:

    PROB_FREQUENCY_SECS = 60

    def __init__(self) -> None:
        # i2c = board.I2C()
        i2c = board.STEMMA_I2C()  # type: ignore
        scd4x = adafruit_scd4x.SCD4X(i2c)
        scd4x.start_periodic_measurement()
        self.scd4x = scd4x
        self.last_probe = -1000

    def get_airquality(self, now: float) -> Airquality | None:
        time_after_last_probe = now - self.last_probe
        if time_after_last_probe > self.PROB_FREQUENCY_SECS:
            if self.scd4x.data_ready:
                co2 = self.scd4x.CO2
                temp = self.scd4x.temperature
                hum = self.scd4x.relative_humidity

                self.last_probe = now
                return Airquality(co2, temp, hum)


def main() -> None:
    provider = AirqualityProvider()

    while True:
        aq = provider.get_airquality(time.monotonic())
        if aq is not None:
            print("CO2: %d ppm" % aq.co2)
            print("Temperature: %0.1f *C" % aq.temperature)
            print("Humidity: %0.1f %%" % aq.humidity)
        else:
            print("No data yet...")
        print()
        time.sleep(1)


if __name__ == "__main__":
    main()
