from machine import ADC, Pin
import time


def main() -> None:
    print("Starting...")

    # Lit internal led to show activity...
    internal_led = Pin(5, Pin.OUT)
    for i in range(5):
        internal_led.value(1)
        time.sleep(0.2)
        internal_led.value(0)
        time.sleep(0.2) 

    print("Powering sensor...")
    # Pin for digital power (3.3V) "VCC"
    power_pin = Pin(5, Pin.OUT)
    power_pin.value(1)

    print("Preparing reading...")
    # Pin for analog reading "SIG"
    sensor_analog_pin = ADC(Pin(25))
    sensor_analog_pin.atten(ADC.ATTN_11DB)  # Full range: 3.3 Volt

    print("Waiting 3 seconds...")
    time.sleep(3)
    # Taking 5 reads every second
    measurements = []
    avg_value = -1
    while len(measurements) < 5:
        # Value range 0-4095 (12-bit)
        raw_val = sensor_analog_pin.read()
        measurements.append(raw_val)
        time.sleep(1)
        print(f"Raw value No. {len(measurements)}: {raw_val}")

    avg_value = sum(measurements) // len(measurements)
    print(f"Averaged value: {avg_value}")

    print("Shutting down sensor...")
    power_pin.value(0)
                

if __name__ == "__main__":
    main()
