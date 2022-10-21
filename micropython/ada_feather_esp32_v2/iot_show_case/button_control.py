import machine
import time
import _thread


class ButtonControl:
    LED_ON = 1
    LED_OFF = 0

    def __init__(self, callback: callable) -> None:
        self.keep_alive = True
        self.callback = callback
        self.button_active = False
        self.push_button = machine.Pin(38, machine.Pin.IN, machine.Pin.PULL_UP)
        self.int_led = machine.Pin(13, machine.Pin.OUT)
        self.int_led.value(ButtonControl.LED_OFF)
        empty_tuple = ((),)
        _thread.start_new_thread(self.run, empty_tuple)

    def run(self, empty_tuple: tuple) -> None:
        print("Button Control is ready and waiting for button action...")
        while self.keep_alive:
            if self.push_button.value() == 0:
                self.button_active = not self.button_active
                print(f"Button pressed. New state: {self.button_active}")
                self.int_led.value(self.button_active)
                time.sleep(0.1)
                if self.button_active:
                    self.int_led.value(ButtonControl.LED_ON)
                    self.callback(True)
                else:
                    self.int_led.value(ButtonControl.LED_OFF)
                    self.callback(False)
                while self.push_button.value() == 0:
                    pass
            time.sleep(0.01)
        print("Button Control is shutting down...")

    def stop(self) -> None:
        self.keep_alive = False
        self.int_led.value(ButtonControl.LED_OFF)
        print("Button Control is stopped.")


def main() -> None:

    def callback_function(button_active: bool) -> None:
        print(f"Callback function: Button active={button_active}")

    button_control = ButtonControl(callback_function)
    print("Waiting for 10 seconds..")
    time.sleep(10)
    print("Stopping Button Control...")
    button_control.stop()


if __name__ == "__main__":
    main()
