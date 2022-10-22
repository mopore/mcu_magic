# circup install adafruit_scd4x
# circup install adafruit_vl53l1x
# circup install adafruit_bh1750

from jni_motion_provider import MotionEvent, MotionProvider
from jni_aq_provider import Airquality, AirqualityProvider
from jni_lightlevel_provider import LightlevelProvider


class SensorData:

	def __init__(
		self, 
		motion_event: MotionEvent | None,
		light_level: float, 
		aq: Airquality | None,
	) -> None:
		self.motion_event = motion_event
		self.light_level = light_level
		self.aq = aq


class SensorStation:
	def __init__(self) -> None:
		self.motion_provider = MotionProvider()
		self.aq_provider: AirqualityProvider | None = None
		try:
			self.aq_provider = AirqualityProvider()
		except Exception as e:
			print(f"Could not find an air quality provider: {e}")
		self.light_provider = LightlevelProvider()

	def collect_data(self) -> SensorData:
		motion_event = self.motion_provider.get_motion()
		light_level = self.light_provider.get_lightlevel()
		aq: Airquality | None = None
		if self.aq_provider is not None:
			aq = self.aq_provider.get_airquality()
		data = SensorData(motion_event, light_level, aq)
		return data

	def provides_air_quality(self) -> bool:
		answer = self.aq_provider is not None
		return answer
