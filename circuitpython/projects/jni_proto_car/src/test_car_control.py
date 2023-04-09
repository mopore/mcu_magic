import asyncio
import time
import jni_input_control
import jni_car_control
import random


async def fake_input_insert(input_control: jni_input_control.InputControl):
	throttle_duration = 3

	start = time.monotonic()
	keep_running = True
	while keep_running:
		time_passed = time.monotonic() - start
		if time_passed > throttle_duration:
			keep_running = False
		else:
			steering_input = 0
			# steering_input = random.uniform(-1, 0)
			throttle_input = 0.5
			# throttle_input = random.uniform(0.5, 1)
			input_control.take_input(steering_input, throttle_input)
			await asyncio.sleep(.2)
	input_control.take_input(0, 0)
	await asyncio.sleep(0.5)
	input_control.take_input(0, 0)


async def main() -> None:
	car_control = jni_car_control.CarControl("test_service", None, dry_mode=True)
	
	input_task = asyncio.create_task(fake_input_insert(car_control._input_control))
	car_control_task = asyncio.create_task(car_control.loop_async())
	await asyncio.gather(input_task, car_control_task)

if __name__ == "__main__":
	asyncio.run(main())
