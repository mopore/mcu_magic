import jni_engine_calibration
from jni_global_settings import REFRESH_RATE_HZ


class EngineManagement:
	
	def __init__(self):
		self.calibration = jni_engine_calibration.EngineCalibration()
		self.x_power = 0
		self.y_power = 0
		self.x_max_change_rate = (1 / REFRESH_RATE_HZ) * 1
		self.y_max_change_rate = (1 / REFRESH_RATE_HZ) * 1
	
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

	def loop(self, x_demand: float, y_demand: float) -> None:
		self.mitigate_steering(x_demand)
		self.mitigate_throttle(y_demand)
		print(f"Powering engines with x={self.x_power}, y={self.y_power}")

		self.calibration.front_left.control(self.y_power)
		self.calibration.front_right.control(self.y_power)
		self.calibration.steering.control(self.x_power)
