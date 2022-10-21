# circup install adafruit_scd4x
# circup install adafruit_vl53l1x
# circup install adafruit_bh1750

import time

from jni_distance_provider import DistanceProvider
from jni_aq_provider import Airquality, AirqualityProvider
from jni_lightlevel_provider import LightlevelProvider


class SensorData:

	def __init__(
		self, distance: float | None, 
		light_level: float, 
		aq: Airquality | None) -> None:
		self.distance = distance
		self.light_level = light_level
		self.aq = aq


class SensorStation:
	def __init__(self) -> None:
		self.distance_provider = DistanceProvider()
		self.aq_provider = AirqualityProvider()
		self.light_provider = LightlevelProvider()

	def collect_data(self) -> SensorData:
		distance = self.distance_provider.get_distance()
		light_level = self.light_provider.get_lightlevel()
		aq = self.aq_provider.get_airquality()
		data = SensorData(distance, light_level, aq)
		return data


