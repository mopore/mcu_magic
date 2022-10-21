import machine
import sys
import utime
import _thread


def main() -> None:
    LED_ON = 1
    LED_OFF = 0

    # Pin definitions
    zero_button = machine.Pin(38, machine.Pin.IN, machine.Pin.PULL_UP)
    int_led = machine.Pin(13, machine.Pin.OUT)

    int_led.value(LED_OFF)
    blink_fast = True
    change_counter = 0
    keep_alive = True

    def blink(empty_tuple):
        print("Starting blinking...")
        while keep_alive:
            if blink_fast:
                int_led.value(LED_ON)
                utime.sleep_ms(100)
                int_led.value(LED_OFF)
                utime.sleep_ms(100)
            else:
                int_led.value(LED_ON)
                utime.sleep_ms(400)
                int_led.value(LED_OFF)
                utime.sleep_ms(100)

    # Blink led 1 second for greeting...
    int_led.value(LED_ON)
    utime.sleep_ms(1000)
    int_led.value(LED_OFF)

    print("Ready for button 38 pushes...")
    while True:
        if zero_button.value() == 0:
            change_counter = change_counter + 1
            if change_counter > 3:
                break

            print(f"Zero button pressed {change_counter} times.")
            blink_fast = not blink_fast
            if change_counter == 1:
                print("Button pressed for 1st time.")
                empty_tuple = ((),)
                _thread.start_new_thread(blink, empty_tuple)
            utime.sleep_ms(1000)
        utime.sleep_ms(100)

    # After while loop break
    print("Already changed three times will reset...")
    keep_alive = False
    print("Reset in 3 seconds...")
    utime.sleep_ms(3000)
    print("Press reset button on device.")
    sys.exit()


if __name__ == "__main__":
    main()
