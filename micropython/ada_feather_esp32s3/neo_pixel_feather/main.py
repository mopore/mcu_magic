import time, neopixel, machine

rainbow_colors = {
    'red': (255, 0, 0),
    'orange': (255, 165, 0),
    'yellow': (255, 255, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'indigo': (75, 0, 130),
    'violet': (238, 130, 238)
}

def main()->None:
    print("Testing NeoPixel")

    print("Powering on NEOPIXEL_I2C_POWER pin...")
    power_pin = machine.Pin(21, machine.Pin.OUT)
    power_pin.value(1)

    print("Preparing neopixel...")
    n = 1
    p = machine.Pin(33, machine.Pin.OUT)
    np = neopixel.NeoPixel(p, n)

    print("Starting demo...")

    for key in rainbow_colors:
        print(f"Setting color to '{key}'")
        np[0] = rainbow_colors[key]
        np.write()
        time.sleep(0.3)

    power_pin.value(0)

    print("All Done!")


if __name__ == "__main__":
    main()
