import json
import time


class InputControl:
	
	INPUT_DEAD_THRESHOLD_SECS = 1
	
	def __init__(self) -> None:
		self._last_input_time = 0
		self._last_x = 0
		self._last_y = 0

	def take_json_input(self, json_input: str) -> None:
		dict_from_json = json.loads(json_input)
		x: float = dict_from_json["x"]
		y: float = dict_from_json["y"]
		self.take_input(x, y)

	def take_input(self, x: float, y: float) -> None:
		self._last_x = x
		self._last_y = y
		self._last_input_time = time.monotonic()

	def get_demands(self) -> tuple[float, float]:
		return self._last_x, self._last_y

	def loop(self) -> None:
		time_passed = time.monotonic() - self._last_input_time
		if time_passed > self.INPUT_DEAD_THRESHOLD_SECS:
			self._last_x = 0
			self._last_y = 0
