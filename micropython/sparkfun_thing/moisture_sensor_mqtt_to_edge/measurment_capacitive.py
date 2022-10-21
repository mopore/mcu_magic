from machine import Pin, SoftI2C
from stemma_soil_sensor import StemmaSoilSensor
import time


def main() -> None:
    print("Starting...")

    # Lit internal led to show activity...
    internal_led = Pin(5, Pin.OUT)
    for _ in range(5):
        internal_led.value(1)
        time.sleep(0.2)
        internal_led.value(0)
        time.sleep(0.2) 

    print("Preparing reading...")
    SDA_PIN = 21
    SCL_PIN = 22
    i2c = SoftI2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN))
    seesaw = StemmaSoilSensor(i2c)

    print("Waiting 3 seconds...")
    time.sleep(3)
    # Taking 5 reads every second
    measurements = []
    avg_value = -1
    while len(measurements) < 5:
        # Value range 0-4095 (12-bit)
        # get moisture
        moisture = seesaw.get_moisture()

        # get temperature
        # temperature = seesaw.get_temp()
        measurements.append(moisture)
        time.sleep(1)
        print(f"Raw value No. {len(measurements)}: {moisture}")

    avg_value = sum(measurements) // len(measurements)
    print(f"Averaged value: {avg_value}")


if __name__ == "__main__":
    main()
