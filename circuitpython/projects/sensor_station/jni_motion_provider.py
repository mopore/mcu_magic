from jni_distance_provider import DistanceMotionEventProvider
from jni_motion_types import MotionEventProvider, MotionEvent
from jni_pir_provider import PirMotionEventProvider


class MotionProvider:

	def __init__(self) -> None:
		event_provider: MotionEventProvider | None = None
		try:
			event_provider = DistanceMotionEventProvider()
		except Exception as e:
			print(f"Could not get a distance motion event provider: {e}")
		if event_provider is None:
			print("Searching for PIR motion event provider...")
			event_provider = PirMotionEventProvider()
			print("PIR motion event provider found")	
		if event_provider is None:
			raise Exception("Could not find a motion event provider!")
		self.event_provider = event_provider

	def get_motion(self) -> MotionEvent | None:
		motion_event = self.event_provider.get_motion_event()
		return motion_event
