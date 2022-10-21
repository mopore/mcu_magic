import machine
import time


def main() -> None:
    # Put an led on the marked Pin 13
    ext_led = machine.Pin(13, machine.Pin.OUT)
    ext_button = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)

    ON_STATE = 1
    OFF_STATE = 0
    BUTTON_PRESSED = 0
    BUTTON_RELEASED = 1

    print("Starting external LED and button...")
    ext_led.value(OFF_STATE)
    button_state_down = False
    while True:
        if button_state_down:
            if BUTTON_RELEASED == ext_button.value():
                print("Button released")    
                ext_led.value(OFF_STATE)
                button_state_down = False 
        else:
            if BUTTON_PRESSED == ext_button.value():
                print("Button pressed!")
                ext_led.value(ON_STATE)
                button_state_down = True 
        time.sleep(0.1)


if __name__ == "__main__":
    main()
