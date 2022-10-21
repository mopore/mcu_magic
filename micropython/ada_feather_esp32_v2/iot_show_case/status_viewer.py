import time, neopixel, machine
import _thread, time


class StatusViewer:
    POWER_ON = 1
    POWER_OFF = 0

    STATE_START = 0
    STATE_IDLE = 1
    STATE_DONE = 2
    STATE_ERROR = 3
    STATE_PREP_AP = 4
    STATE_AWAIT_CLIENT = 5
    STATE_OPERATIVE = 6

    COLORS = {
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'orange': (255, 165, 0),
        'yellow': (200, 200, 0),
        'green': (0, 25, 0),
        'blue': (0, 0, 20),
        'indigo': (75, 0, 130),
        'violet': (138, 30, 138)
    }

    def __init__(self):
        # Powering on NEOPIXEL_I2C_POWER pin...
        self.power_pin = machine.Pin(2, machine.Pin.OUT)
        self.power_pin.value(StatusViewer.POWER_ON)

        # Preparing neopixel...
        n = 1
        p = machine.Pin(0, machine.Pin.OUT)
        self.np = neopixel.NeoPixel(p, n)

        self.viewing_state = StatusViewer.STATE_START

        self.keep_alive = True
        self.tick = 0
        empty_tuple = ((),)
        _thread.start_new_thread(self.run, empty_tuple)

    def run(self, empty_tuple: tuple) -> None:
        print("StatusViewer is ready and waiting for viewing tasks...")
        self.viewing_state = StatusViewer.STATE_IDLE
        self.view_start()
        while self.keep_alive:
            if self.viewing_state == StatusViewer.STATE_IDLE:
                self.view_idle()
            elif self.viewing_state == StatusViewer.STATE_ERROR:
                self.view_error()
            elif self.viewing_state == StatusViewer.STATE_PREP_AP:
                self.view_prep_ap()
            elif self.viewing_state == StatusViewer.STATE_AWAIT_CLIENT:
                self.view_await_client()
            elif self.viewing_state == StatusViewer.STATE_OPERATIVE:
                self.view_operative()
            time.sleep(0.1)
            self.tick += 1
            if self.tick == 20:
                self.tick = 0
        # keep_alive is no longer True 
        print("StatusViewer is shutting down...")
        self.view_done()
        self.power_pin.value(StatusViewer.POWER_OFF)

    def view_start(self) -> None:
        for i in range(25):
            self.np[0] = (0, i, 0)
            self.np.write()
            time.sleep(0.1)

    def to_idle(self) -> None:
        self.viewing_state = StatusViewer.STATE_IDLE
            
    def view_idle(self) -> None:
        if self.tick > 16:
            self.np[0] = StatusViewer.COLORS["blue"]
        else:
            self.np[0] = StatusViewer.COLORS["black"]
        self.np.write()

    def to_error(self) -> None:
        self.viewing_state = StatusViewer.STATE_ERROR

    def view_error(self) -> None:
        if self.tick % 2 == 0:
            self.np[0] = StatusViewer.COLORS["yellow"]
        else:
            self.np[0] = StatusViewer.COLORS["black"]
        self.np.write()

    def to_prep_ap(self) -> None:
        self.viewing_state = StatusViewer.STATE_PREP_AP

    def view_prep_ap(self) -> None:
        if (self.tick < 5) or (self.tick > 10 and self.tick < 15):
            self.np[0] = StatusViewer.COLORS["indigo"]
        else:
            self.np[0] = StatusViewer.COLORS["black"]
        self.np.write()

    def view_await_client(self) -> None:
        if self.tick in (0, 1, 6, 7):
            self.np[0] = StatusViewer.COLORS["violet"]
        else:
            self.np[0] = StatusViewer.COLORS["black"]
        self.np.write()

    def view_operative(self) -> None:
        self.np[0] = StatusViewer.COLORS["green"]
        self.np.write()

    def to_await_client(self) -> None:
        self.viewing_state = StatusViewer.STATE_AWAIT_CLIENT

    def to_operative(self) -> None:
        self.viewing_state = StatusViewer.STATE_OPERATIVE

    def shutdown(self) -> None:
        self.viewing_state = StatusViewer.STATE_DONE
        self.keep_alive = False

    def view_done(self) -> None:
        for i in range(255, -1, -1):
            self.np[0] = (i, 0, 0)
            self.np.write()
            time.sleep(0.005)


def main() -> None:
    int_led = machine.Pin(13, machine.Pin.OUT)
    int_led.value(StatusViewer.POWER_OFF)

    print("Starting StatusViewer")
    viewer = StatusViewer()
    print("Idle state for 5 seconds")
    time.sleep(5)

    print("Error state for 3 seconds")
    viewer.to_error()
    time.sleep(3)

    print("Idle for 3 seconds")
    viewer.to_idle()
    time.sleep(3)

    print("Prep AP state for 3 seconds")
    viewer.to_prep_ap()
    time.sleep(3)

    print("Await client state for 3 seconds")
    viewer.to_await_client()
    time.sleep(3)

    print("Operative state for 3 seconds")
    viewer.to_operative()
    time.sleep(3)

    print("Stopping StatusViewer")
    viewer.shutdown()
    print("All Done!")


if __name__ == "__main__":
    main()