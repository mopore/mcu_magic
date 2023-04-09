import asyncio
import time
import jni_car_control
import jni_input_control
import random


async def fake_input(input_control: jni_input_control.InputControl):
	throttle_duration = 5

	start = time.monotonic()
	keep_running = True
	while keep_running:
		time_passed = time.monotonic() - start
		if time_passed > throttle_duration:
			keep_running = False
		else:
			throttle_input = random.uniform(0.5, 1)
			input_control.take_input(0, throttle_input)
			await asyncio.sleep(.2)
	input_control.take_input(0, 0)


async def main() -> None:
	service_name = "test_service"
	car_control = jni_car_control.CarControl(service_name, dry_mode=True)
	car_control_task = asyncio.create_task(car_control.loop_async())
	fake_input_task = asyncio.create_task(fake_input(car_control.input_control))
	await asyncio.gather(car_control_task, fake_input_task)


if __name__ == "__main__":
	asyncio.run(main())
