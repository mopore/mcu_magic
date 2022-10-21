import time


class MotionEventReceiver():

	def on_new_motion(self) -> None:
		...

	def on_motion_gone(self) -> None:
		...


class MotionHandler:

	TRIGGER_DISTANCE_CM = 200
	NEW_MOTION_TIME_THRESHOLD = 6
	INIT_VALUE = -1

	def __init__(self, motionReceiver: MotionEventReceiver) -> None:
		self.motion_receiver = motionReceiver
		self.last_new_motion_timestamp = 0
		self.current_motion = False
		self.last_reading: None | float = self.INIT_VALUE

	def handle_distance_data(self, reading: float | None) -> None:
		if self.last_reading == self.INIT_VALUE:
			self.last_reading = reading
		movement_now = False
		if reading is not None and reading < self.TRIGGER_DISTANCE_CM:
			if self.last_reading is None:
				movement_now = True
				self._when_movement_now()
			else:    
				# Check if not a static object is present
				diff = self.last_reading - reading
				if abs(diff) > 2: 
					movement_now = True
					self._when_movement_now()
		if movement_now is False and self.current_motion is True:
			current_timestamp = time.time()
			time_after_trigger = current_timestamp - self.last_new_motion_timestamp
			if time_after_trigger > self.NEW_MOTION_TIME_THRESHOLD:
				self.current_motion = False
				self.motion_receiver.on_motion_gone() 
		# time.sleep(0.5)
		self.last_reading = reading
	
	def _when_movement_now(self) -> None:
		try:
			self.last_new_motion_timestamp = time.time()
			if self.current_motion is False:
				self.current_motion = True
				self.motion_receiver.on_new_motion()
		except Exception as e:
			error_message = f"Error with Motion Handler when handling motion: {e}"
			raise Exception(error_message)
