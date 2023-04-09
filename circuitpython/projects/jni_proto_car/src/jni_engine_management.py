import jni_engine_calibration
from jni_global_settings import REFRESH_RATE_HZ


class EngineManagement:

	def __init__(self, dry_mode: bool = False):
		self.calibration = jni_engine_calibration.EngineCalibration()
		self.dry_mode = dry_mode
		self.x_power = 0
		self.y_power = 0
		self.x_max_change_rate = (1 / REFRESH_RATE_HZ) * 1
		self.y_max_change_rate = (1 / REFRESH_RATE_HZ) * 1
		self.panic_stop_time = -1
	
	def mitigate_throttle(self, y_demand: float) -> None:
		demanded_change = y_demand - self.y_power
		if abs(demanded_change) > self.y_max_change_rate:
			if demanded_change > 0:
				self.y_power += self.y_max_change_rate
			else:
				self.y_power -= self.y_max_change_rate
		else:
			self.y_power = y_demand
	
	def mitigate_steering(self, x_demand: float) -> None:
		demanded_change = x_demand - self.x_power
		if abs(demanded_change) > self.x_max_change_rate:
			if demanded_change > 0:
				self.x_power += self.x_max_change_rate
			else:
				self.x_power -= self.x_max_change_rate
		else:
			self.x_power = x_demand

	def panic_stop(self) -> None:
		self.y_power = 0
		self.panic_mode = True
		if self.dry_mode:
			print("Dry: Panic stop")
		else:
			self.calibration.front_left.control(self.y_power)
			self.calibration.front_right.control(self.y_power)
	
	def loop(self, x_demand: float, y_demand: float) -> None:
		if not self.panic_mode:
			self.mitigate_steering(x_demand)
			self.mitigate_throttle(y_demand)
			
			if self.dry_mode:
				front_left = self.y_power * 100
				front_right = self.y_power * 100
				steering = self.x_power * 100
				print(f"Dry: FL {front_left:.0f}%, FR {front_right:.0f}%, " +
				f"Steering {steering:.0f}%")
			else:
				self.calibration.front_left.control(self.y_power)
				self.calibration.front_right.control(self.y_power)
				self.calibration.steering.control(self.x_power)
