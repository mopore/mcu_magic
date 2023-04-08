import asyncio
import time
import jni_car_control
import jni_input_control


async def fake_input(input_control: jni_input_control.InputControl):
	start = time.monotonic()
	keep_running = True
	print("Faking 3 seconds of full input")
	while keep_running:
		time_passed = time.monotonic() - start
		if time_passed > 3:
			keep_running = False
		else:
			input_control.take_input(0, 1)
			await asyncio.sleep(.2)
	print("Input to 0...")
	input_control.take_input(0, 0)
	print("Done.")


async def main() -> None:
	service_name = "test_service"
	car_control = jni_car_control.CarControl(service_name)
	car_control_task = asyncio.create_task(car_control.loop_async())
	fake_input_task = asyncio.create_task(fake_input(car_control.input_control))
	await asyncio.gather(car_control_task, fake_input_task)


if __name__ == "__main__":
	asyncio.run(main())
