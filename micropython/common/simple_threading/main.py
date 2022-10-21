import _thread
import time


counter = 0

class Counter:

    def __init__(self):
        self.counter = 0
        self.keep_alive = True
        empty_tuple = ((),)
        _thread.start_new_thread(self.run, empty_tuple)

    def run(self, empty_tuple) -> None:
        while self.keep_alive:
            self.counter += 1
            print(f"Thread: Counter is at {self.counter}")
            time.sleep(0.5)
        print("Thread: I am done.")


def main() -> None:
    print("Main: Starting counter thread...")
    counter = Counter()
    print("Main: Will stop in 3 seconds.") 
    time.sleep(3) 
    print("Main: Infomrming counter to stop.")
    counter.keep_alive = False
    print("Main: Main will end now.")

if __name__ == "__main__":
    main()
