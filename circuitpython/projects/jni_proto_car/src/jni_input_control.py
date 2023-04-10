import socket
import time


def calculate_value_change(thresholds: list[float]) -> float:
	# Take the threshold list, test and identify the equal gap between the thresholds
	gap = thresholds[1] - thresholds[0]  # Take the first gap as a probe
	for i in range(1, len(thresholds) - 1):
		if thresholds[i + 1] - thresholds[i] != gap:
			raise Exception("Error: thresholds are not equidistant")
	return gap
	

class InputControl:
	""" 
	The main purpose of the value smoothing in this class is to prevent instable input to the
	servo motors. There are two approaches implemented:
	1. A change of values is only accepteted when the input values follow a trend in a row 
	of four values.
	2. Mapping all input to a set of thresholds is the 2nd way to make the input more stable
	"""
	
	INPUT_DEAD_THRESHOLD_SECS = 1
	VALUE_THRESHOLDS = [-1, -0.75, -0.5, -0.25, 0, .25, .5, .75, 1]
	VALUE_CHANGE = calculate_value_change(VALUE_THRESHOLDS)
	
	def __init__(self) -> None:
		self._last_input_time = 0
		self._x_trends: list[float] = [0, 0, 0, 0]
		self._y_trends: list[float] = [0, 0, 0, 0]
		self._last_x_input = 0
		self._last_y_input = 0
		self._last_x_output = 0
		self._last_y_output = 0

	def take_mqtt_input(self, raw_input: str) -> None:
		x_raw, y_raw = raw_input.split(",")
		x = float(x_raw) / 100
		y = float(y_raw) / 100
		self.take_input(x, y)

	def take_input(self, input_x: float, input_y: float) -> None:
		smoothed_x, smoothed_y = self._smooth_inputs(input_x, input_y)
		self._last_x_input = smoothed_x
		self._last_y_input = smoothed_y
		self._last_input_time = time.monotonic()

	def get_demands(self) -> tuple[float, float]:
		smooth_x = self._smooth_output(self._last_x_input, self._last_x_output, self._x_trends)
		smooth_y = self._smooth_output(self._last_y_input, self._last_y_output, self._y_trends)

		self._last_x_output = smooth_x
		self._last_y_output = smooth_y
		return self._last_x_output, self._last_y_output

	def loop(self) -> None:
		time_passed = time.monotonic() - self._last_input_time
		if time_passed > self.INPUT_DEAD_THRESHOLD_SECS:
			# Cut throttle demand due to missing input
			self._last_y_input = 0
			self._last_y_output = 0
			self._y_trends = [0, 0, 0, 0]
			# We do not touch the steering to avoid further problems after input is lost

	def _smooth_inputs(self, raww_input_x: float, raw_input_y: float) -> tuple[float, float]:
		smoothed_x = self._nearest_threshold(raww_input_x)
		smoothed_y = self._nearest_threshold(raw_input_y)

		x_trend = self._calculate_trend(smoothed_x, self._last_x_output)
		self._x_trends.pop(0)
		self._x_trends.append(x_trend)
		y_trend = self._calculate_trend(smoothed_y, self._last_y_output)
		self._y_trends.pop(0)
		self._y_trends.append(y_trend)

		return smoothed_x, smoothed_y

	def _binary_search_index(self, value) -> int:
		low, high = 0, len(self.VALUE_THRESHOLDS)

		while low < high:
			mid = (low + high) // 2
			if self.VALUE_THRESHOLDS[mid] < value:
				low = mid + 1
			else:
				high = mid

		return low

	def _nearest_threshold(self, value) -> float:

		# Find the index where value would be inserted in the sorted list
		index = self._binary_search_index(value)

		# Get the nearest threshold by comparing with the left neighbor
		left_neighbor = self.VALUE_THRESHOLDS[index - 1]
		if abs(value - left_neighbor) <= abs(value - self.VALUE_THRESHOLDS[index]):
			return left_neighbor
		else:
			return self.VALUE_THRESHOLDS[index]
	
	def _calculate_trend(self, new: float, old: float) -> float:
		if new == old:
			return 0
		elif new > old:
			return 1
		else:
			return -1

	def _smooth_output(self, last_input: float, last_output: float, trends: list[float]) -> float:
		if last_input == last_output:
			return last_output
		else:
			trend = sum(trends)
			if trend == 0:
				return last_output
			elif trend >= 2:
				if last_output == 1:
					return last_output
				return last_output + self.VALUE_CHANGE
			elif trend <= -2:
				if last_output == -1:
					return last_output
				return last_output - self.VALUE_CHANGE
			else:
				return last_output

def main() -> None:
   server_socket = socket.socket.AF_INET, socket.SOCK_STREAM)
   
   server_address = ('localhost', 3000)') 