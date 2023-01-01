import time
import displayio
import board

import adafruit_displayio_sh1107


def activate_oled_when_present() -> bool:
    try:
        WIDTH = 128
        HEIGHT = 64
        displayio.release_displays()
        i2c = board.I2C()
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
        return True
    except Exception as err:
        return False


def main() -> None:
    display_activated = activate_oled_when_present()
    if display_activated:
        print("Display activated")
    else:
        print("Could not find a display.")

    while True:
        uptime = time.monotonic()
        print(f"Uptime: {uptime:.1f}s")
        time.sleep(5)


if __name__ == "__main__":
    main()

