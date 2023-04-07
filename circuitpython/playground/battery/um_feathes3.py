import time
import feathers3


def get_power_info() -> str: 
    on_usbc_power = feathers3.get_vbus_present()
    if on_usbc_power:
        return "USB-C connected."
    else:
        battery_voltage = feathers3.get_battery_voltage()
        return f"Battery: {battery_voltage:.1f}V" 


def main() -> None:
    while True:
        power_info = get_power_info()
        print(power_info)
        time.sleep(1)


if __name__ == "__main__":
    main()
