from jni_distance_provider import DistanceMotionEventProvider
from jni_motion_types import MotionEventProvider 
from jni_pir_provider import PirMotionEventProvider
import neopixel


class MotionProvider:

	def __init__(self, np: neopixel.NEOPIXEL) -> None:
		event_provider: MotionEventProvider | None = None
		try:
			event_provider = DistanceMotionEventProvider(np)
		except Exception as e:
			print(f"Could not get a distance motion event provider: {e}")
			raise e
		if event_provider is None:
			print("Searching for PIR motion event provider...")
			event_provider = PirMotionEventProvider()
			print("PIR motion event provider found")
		if event_provider is None:
			raise Exception("Could not find a motion event provider!")
		self.event_provider = event_provider

	def get_motion(self):
		result = self.event_provider.get_motion_event()
		if result is None:
			return None
		else:
			return result
