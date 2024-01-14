class MotionEvent():

	NEW_MOTION = True
	MOTION_GONE = False

	def __init__(self, new_motion: bool) -> None:
		self.new_motion = new_motion


class MotionEventProvider:

	def get_motion_event(self) -> (MotionEvent, str) | None:
		...
