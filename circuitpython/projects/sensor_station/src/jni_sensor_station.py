# circup install adafruit_scd4x
# circup install adafruit_vl53l1x
# circup install adafruit_bh1750

from jni_motion_types import MotionEvent
from jni_motion_provider import MotionProvider
from jni_aq_provider import Airquality, AirqualityProvider
from jni_lightlevel_provider import LightlevelProvider
import neopixel


class SensorData:

	def __init__(
		self,
		motion_event: MotionEvent | None,
		light_level: float | None,
		aq: Airquality | None,
		motion_proof: str | None = None,
	) -> None:
		self.motion_event = motion_event
		self.light_level = light_level
		self.aq = aq
		self.proof = motion_proof


class SensorStation:
	def __init__(self, np: neopixel.NEOPIXEL) -> None:
		self.motion_provider = MotionProvider(np)
		self.aq_provider: AirqualityProvider | None = None
		try:
			self.aq_provider = AirqualityProvider()
		except Exception as e:
			print(f"Could not find an air quality provider: {e}")
		self.light_provider = LightlevelProvider()

	def collect_data(self, fulltick: bool, now: float) -> SensorData:
		motion_result = self.motion_provider.get_motion()
		if motion_result is None:
			motion_event = None
			proof = None
		else:
			motion_event, proof = motion_result

		if fulltick:
			light_level = self.light_provider.get_lightlevel()
			aq: Airquality | None = None
			if self.aq_provider is not None:
				aq = self.aq_provider.get_airquality(now)
			return SensorData(motion_event, light_level, aq, proof)
		else:
			return SensorData(motion_event, None, None, proof)

	def provides_air_quality(self) -> bool:
		answer = self.aq_provider is not None
		return answer
