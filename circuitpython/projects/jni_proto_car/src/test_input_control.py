import asyncio
import time
import jni_input_control
import random


async def fake_input_grepping(input_control: jni_input_control.InputControl) -> None:
	print("x;y")
	while True:
		x_demand, y_demand = input_control.get_demands()		
		x = x_demand * 100
		y = y_demand * 100
		print(f"{x:.0f};{y:.0f}")
		input_control.loop()
		await asyncio.sleep(0.1)


async def fake_input_insert(input_control: jni_input_control.InputControl):
	throttle_duration = 5

	start = time.monotonic()
	keep_running = True
	while keep_running:
		time_passed = time.monotonic() - start
		if time_passed > throttle_duration:
			keep_running = False
		else:
			steering_input = 0
			# steering_input = random.uniform(-1, 0)
			throttle_input = 1
			# throttle_input = random.uniform(0.5, 1)
			input_control.take_input(steering_input, throttle_input)
			await asyncio.sleep(.2)
	# input_control.take_input(0, 0)
	# await asyncio.sleep(0.5)
	# input_control.take_input(0, 0)


async def main() -> None:
	input_control = jni_input_control.InputControl()
	input_task = asyncio.create_task(fake_input_insert(input_control))
	grep_task = asyncio.create_task(fake_input_grepping(input_control))
	await asyncio.gather(input_task, grep_task)


if __name__ == "__main__":
	asyncio.run(main())
