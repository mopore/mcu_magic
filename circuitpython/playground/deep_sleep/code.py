import alarm
import time
# import board
# import digitalio

print("Waking up...")
time.sleep(3)
print("Going in to sleep in...")
for i in range(5, 0, -1):
	print(i)
	time.sleep(1)

# print("Powering down neopixel power")
# neo_power_pin = digitalio.DigitalInOut(board.NEOPIXEL_POWER)  # type: ignore
# neo_power_pin.direction = digitalio.Direction.OUTPUT
# neo_power_pin.value = False

# print("Powering down display")
# tft_power_pin = digitalio.DigitalInOut(board.TFT_I2C_POWER)  # type: ignore
# tft_power_pin.direction = digitalio.Direction.OUTPUT
# tft_power_pin.value = False

monotonic = time.monotonic() + 7
time_alarm = alarm.time.TimeAlarm(monotonic_time=monotonic)
alarm.exit_and_deep_sleep_until_alarms(time_alarm)
