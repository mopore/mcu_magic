import uasyncio


class TestRunner:
    def __init__(self, name, sleep_interval):
        self.name = name
        self.counter = 0
        self.sleep_interval = sleep_interval
        self.keep_running = True
        uasyncio.create_task(self.run())

    async def run(self):
        while self.keep_running:
            self.counter += 1
            print(f"{self.name} ({self.counter}): Running...")
            if self.counter == 3:
                self.keep_running = False
            else:
                await uasyncio.sleep(self.sleep_interval)
        print(f"{self.name}: Completed")


async def main():
    print("Starting runners for 3 steps...")
    runner1 = TestRunner("Eager", 1)
    runner2 = TestRunner("Lazy", 3)
    while runner1.keep_running or runner2.keep_running:
        await uasyncio.sleep(1)
    print("All done")


if __name__ == "__main__":
    uasyncio.run(main())
