import board
import neopixel
import time
import asyncio

import jni_distance_provider
import jni_noods_enlighter
import jni_wardrobe_mqtt_bridge
import jni_temp_provider


NOODS_ON = True
NOODS_OFF = False

TEMP_REFRESH_INTERVAL_SEC = 10


class ThresholdProvider:

	STATE_AWAITING_STABLE_VALUE = 0
	STATE_CALIBRATED = 1

	NO_MOVE_THRESHOLD_CM = 3
	STABLE_FOR_CALIBRATION_SEC = 10

	NP_GREEN = (0, 255, 0)
	NP_RED = (255, 0, 0)
	NP_BLACK = (0, 0, 0)

	def __init__(self) -> None:
		self.state = self.STATE_AWAITING_STABLE_VALUE
		self.last_distance = -1
		self.last_distance_time = 0
		self.distance_threshold = -1
		self.onboard_np = neopixel.NeoPixel(board.NEOPIXEL, 1)  # type: ignore
		self.onboard_np.brightness = 0.03
		self.onboard_np.fill(self.NP_GREEN)

	def calibrate(self, distance: float) -> None:
		now = time.monotonic()
		if self.last_distance < 0:
			self.last_distance = distance
			self.last_distance_time = now
			print("Waiting for stable value for door threshold...")
		else:
			if self.STATE_AWAITING_STABLE_VALUE == self.state:
				diff = abs(self.last_distance - distance)
				
				if diff < self.NO_MOVE_THRESHOLD_CM:
					self.onboard_np.fill(self.NP_GREEN)
					time_passed = now - self.last_distance_time
					if time_passed > self.STABLE_FOR_CALIBRATION_SEC:
						self.distance_threshold = distance
						self.onboard_np.fill(self.NP_BLACK)
						self.onboard_np.brightness = 0
						self.last_noods_off = time.monotonic()
						self.state = self.STATE_CALIBRATED
						print(f"Threshold calibrated to {distance}")
				else:
					self.onboard_np.fill(self.NP_RED)
					self.last_distance = distance
					self.last_distance_time = now

	def get_desired_state(self, distance: float) -> bool:
		if distance - self.NO_MOVE_THRESHOLD_CM > self.distance_threshold:
			return NOODS_ON
		else:
			return NOODS_OFF


class WardrobeMain:
	
	def __init__(self, mqtt_brdige: jni_wardrobe_mqtt_bridge.WardrobeMqttBridge) -> None:
		self.dp = jni_distance_provider.DistanceProvider()
		pin = board.MOSI  # Adafruit QT Py ESP32-S3
		self.enligher = jni_noods_enlighter.NoodsEnlighter(pin)
		self.tProvider = ThresholdProvider()
		self.tempProvider = jni_temp_provider.TemperatureProvider()
		self.mqtt = mqtt_brdige
		self.last_temp_time = time.monotonic()
	
	def check__temperature_update(self) -> None:
		now = time.monotonic()
		timepassed = now - self.last_temp_time
		if timepassed > TEMP_REFRESH_INTERVAL_SEC:
			self.last_temp_time = now
			temp = self.tempProvider.read_temperature()
			if temp is not None:
				self.mqtt.update_temperature(temp)
	
	async def loop_async(self) -> None:
		current_noods_state = NOODS_OFF
		last_turn_off_request: float = 0

		while True:
			distance = self.dp.read_distance()
			if distance is not None:
				needs_calibration = ThresholdProvider.STATE_CALIBRATED != self.tProvider.state
				if needs_calibration:
					self.tProvider.calibrate(distance)
				else:
					desired_noods_state = self.tProvider.get_desired_state(distance)
					if desired_noods_state != current_noods_state:
						if desired_noods_state == NOODS_ON:
							print("Door is open.")
							# The wardrobe is open, turn on the noods.
							last_turn_off_request = 0
							current_noods_state = desired_noods_state
							self.enligher.light_up()
							self.mqtt.update_door_state(True)
						else:
							if last_turn_off_request == 0:
								last_turn_off_request = time.monotonic()
							else:
								time_passed = time.monotonic() - last_turn_off_request
								if time_passed > 1:
									print("Door is closed.")
									# door is closed
									# Wait 1 second for constant turn-off requests to turn off noobs.
									current_noods_state = desired_noods_state
									self.enligher.light_down()
									self.mqtt.update_door_state(False)
							
			self.check__temperature_update()
			await asyncio.sleep(.2)
