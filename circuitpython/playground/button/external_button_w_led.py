# See: https://images.squarespace-cdn.com/content/v1/5a8cc639a803bbfaa029615a/d12e60b8-9864-4b4b-8913-f9fc1fcf80f1/pins_feathers3.jpg?format=1500w

import board
import digitalio
from digitalio import DigitalInOut, Pull

LED_OFF = False
LED_ON = True
BUTTON_IS_PRESSED = False
BUTTON_NOT_PRESSED = True


def main() -> None:
    ext_button = DigitalInOut(board.IO5)  # type: ignore    ext_button.switch_to_input(pull=Pull.UP)
    ext_button.switch_to_input(pull=Pull.UP)
    
    led = digitalio.DigitalInOut(board.IO1)  # UM
    led.direction = digitalio.Direction.OUTPUT
    
    print("Press the button...")
    led.value = LED_OFF
    ready_for_press = True
    while True:
        if ready_for_press:
            if BUTTON_IS_PRESSED == ext_button.value:
                print("Button pressed.")
                led.value = LED_ON
                ready_for_press = False
        else:
            if BUTTON_NOT_PRESSED == ext_button.value:
                print("Button released")
                led.value = LED_OFF
                ready_for_press = True


if __name__ == "__main__":
    main()  
