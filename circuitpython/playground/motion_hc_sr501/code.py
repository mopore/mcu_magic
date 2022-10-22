
import board
import time

from digitalio import DigitalInOut, Pull


class MotionReceiver():

    def on_new_motion(self) -> None:
        ...
    
    def on_motion_gone(self) -> None:
        ...


class MotionSensorHandler():

    MOTION_YES = True
    MOTION_NO = False
    NEW_MOTION_TIME_THRESHOLD = 6
    #  BOARD_PIN = board.D13  # Adafruit TFT Feather name
    BOARD_PIN = board.A0  # Adafruit QT Py ESP32-S3

    def __init__(self, motionReceiver: MotionReceiver):
        self.motion_receiver = motionReceiver
        self.keep_alive = True
        self.okay = True
        
        self.last_new_motion_timestamp = 0
        self.last_motion_trigger = 0
        self.current_motion = self.MOTION_NO
        motion_pin = DigitalInOut(self.BOARD_PIN)  # Adafruit TFT Feather name
        motion_pin.switch_to_input(pull=Pull.UP)
        self.motion_pin = motion_pin
    
    def run(self) -> None:
        while self.keep_alive:
            try:
                if self.motion_pin.value is self.MOTION_YES:
                    self.when_motion()
                if self.current_motion:
                    current_timestamp = time.time()
                    time_after_trigger = current_timestamp - self.last_motion_trigger
                    if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
                        self.current_motion = self.MOTION_NO
                        self.motion_receiver.on_motion_gone() 
            except Exception as e:
                print(f"Error with Motion Sensor Handler when checking motion gone: {e}")
                self.okay = False
        print("Motion Sensor Handler is stopped.")
    
    def when_motion(self) -> None:
        try:
            current_timestamp = time.time()
            self.last_motion_trigger = current_timestamp
            time_after_last_new_motion = current_timestamp - self.last_new_motion_timestamp
            if time_after_last_new_motion > self.NEW_MOTION_TIME_THRESHOLD:
                self.last_new_motion_timestamp = current_timestamp
                if self.current_motion is self.MOTION_NO:
                    self.current_motion = True
                    self.motion_receiver.on_new_motion()
        except Exception as e:
            print(f"Error with Motion Sensor Handler when handling motion: {e}")
            self.okay = False


def main() -> None:
    
    class MyReciever(MotionReceiver):
        def on_new_motion(self) -> None:
            print("New motion!")
        
        def on_motion_gone(self) -> None:
            print("Motion gone!")
    
    handler = MotionSensorHandler(MyReciever())
    print("Handler created and waiting for events...")
    
    while True:
        handler.run()
        time.sleep(0.5)    


if __name__ == "__main__":
    main()
