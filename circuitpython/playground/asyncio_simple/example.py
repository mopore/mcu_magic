#  Ensure to have asyncio installed as a library on the device.
#  pip3 install circup
#  circup install asyncio

import asyncio


class Keyboard:

    def __init__(self):
        self.counter = 0

    async def go(self):
        print("Entering go...")
        while True:
            self.main_loop()
            await asyncio.sleep(0)

    def main_loop(self):
        self.counter += 1

    async def jni_loop(self):
        print("Entering jni loop")
        while True:
            await asyncio.sleep(1)
            print("I have time...")


async def main():
    keyboard = Keyboard()
    print("Creating tasks...")
    go_task = asyncio.create_task(keyboard.go())
    jni_task = asyncio.create_task(keyboard.jni_loop())
    await asyncio.gather(go_task, jni_task)


if __name__ == "__main__":
    print("Preparing main...")
    asyncio.run(main())
