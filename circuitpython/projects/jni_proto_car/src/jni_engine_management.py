import jni_engine_calibration


class EngineManagement:

	def __init__(self, dry_mode: bool = False):
		self._calibration = jni_engine_calibration.EngineCalibration()
		self._dry_mode = dry_mode
		self._panic_mode = False
		self._x_power = 0
		self._y_power = 0
		self._x_max_change_rate = .1  # Change by 10% per tick
		self._y_max_change_rate = .1  # Change by 10% per tick
		self._panic_stop_time = -1
	
	def loop(self, x_demand: float, y_demand: float) -> None:
		if not self._panic_mode:
			self._mitigate_steering(x_demand)
			self._mitigate_throttle(y_demand)
			
			if self._dry_mode:
				front_left = self._y_power * 100
				front_right = self._y_power * 100
				steering = self._x_power * 100
				print(f"Dry: FL {front_left:.0f}%, FR {front_right:.0f}%, " +
				f"Steering {steering:.0f}%")
			else:
				self._calibration.front_left.control(self._y_power)
				self._calibration.front_right.control(self._y_power)
				self._calibration.steering.control(self._x_power)

	def panic_stop(self) -> None:
		self._y_power = 0
		self._panic_mode = True
		if self._dry_mode:
			print("Dry: Panic stop")
		else:
			self._calibration.front_left.control(self._y_power)
			self._calibration.front_right.control(self._y_power)
	
	def _mitigate_throttle(self, y_demand: float) -> None:
		demanded_change = y_demand - self._y_power
		if abs(demanded_change) > self._y_max_change_rate:
			if demanded_change > 0:
				self._y_power += self._y_max_change_rate
			else:
				self._y_power -= self._y_max_change_rate
		else:
			self._y_power = y_demand
	
	def _mitigate_steering(self, x_demand: float) -> None:
		demanded_change = x_demand - self._x_power
		if abs(demanded_change) > self._x_max_change_rate:
			if demanded_change > 0:
				self._x_power += self._x_max_change_rate
			else:
				self._x_power -= self._x_max_change_rate
		else:
			self._x_power = x_demand
