#  circup install adafruit_amg88xx
#  circup install ujson
# Library documentation: https://docs.circuitpython.org/projects/amg88xx/en/latest/api.html
import time
import busio
import board
import adafruit_amg88xx
import json

i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)


def main():
    print("Reading 10 times data from sensor...")
    for _ in range(10):
        print("Raw data from thermo sensor...")
        for row in amg.pixels:
            print(['{0:.1f}'.format(temp) for temp in row])
        print()
        print("Converted to JSON...")
        export = {"sensor_data": amg.pixels} 
        print(json.dumps(export))
        print("\n\n")
        time.sleep(1)


if __name__ == "__main__":
    main()
