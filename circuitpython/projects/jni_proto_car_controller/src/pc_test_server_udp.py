import socket
import struct
import errno
import time
import asyncio

#  LOOP_TIME_BUDGET = 1  # 1 Hz
#  LOOP_TIME_BUDGET = 0.1  # 10 Hz
LOOP_TIME_BUDGET = 0.01  # 100 Hz
#  CHECK_INTEGRITY = True
CHECK_INTEGRITY = False


class UdpServer:

	def __init__(self) -> None:
		self._udp_socket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
		self._udp_socket.setblocking(0)  # type: ignore
		host = '0.0.0.0'  # Listen on all available interfaces
		port = 8080
		self._udp_socket.bind((host, port))
		self._b = bytearray(4)
		self.keep_running = True
		self._last_x = -101
		print("UDP server started")

	def _read_from_client(self) -> None | tuple[int, int]:
		""" Return None if no data is available, otherwise return a tuple of two integers. """
		try:
			self._udp_socket.recv_into(self._b)
			x, y = struct.unpack("<hh", self._b)
			# print("Received data: x =", x, "y =", y)
			return x, y
		except OSError as err:
			if errno.EAGAIN == err.args[0]:
				return None
			else:
				print(f"Error with client sockert: {err}")
				raise err

	def _check_integrity(self, new_x: int) -> None:
		if new_x == -100:
			return
		if new_x <= self._last_x:
			raise Exception(f"Integrity problem: {self._last_x} >= {new_x}")	

	def _read_socket_empty(self) -> None | tuple[int, int]:
		response: None | tuple[int, int] = None
		last_result = self._read_from_client()	
		if last_result is not None:
			response = last_result

		while last_result is not None:
			result = self._read_from_client()
			if result is not None:
				x, y = result
				print(f"Skipping: {x}, {y}")
				response = last_result
			else:
				x, y = last_result
				print(f"using: {x}, {y}")
				last_result = None
		return response

	async def loop_async(self, time_budget: float) -> None:
		while self.keep_running:
			# print("Loop start")
			loop_start_timestamp = time.monotonic()
			result = self._read_socket_empty()
			if result is not None:
				x, y = result
				if CHECK_INTEGRITY:
					self._check_integrity(x)
					self._last_x = x
			now = time.monotonic()
			time_in_loop = now - loop_start_timestamp
			# print(f"Time in loop: {time_in_loop:.3f} s (budget: {time_budget:.0f} s)")
			time_left_in_loop = time_budget - time_in_loop
			if time_left_in_loop > 0:
				await asyncio.sleep(time_left_in_loop)
				# print(f"Sleeping: {time_left_in_loop:.2f} s")


async def main() -> None:
	server = UdpServer()
	server_task = asyncio.create_task(server.loop_async(LOOP_TIME_BUDGET))
	await asyncio.gather(server_task)


if __name__ == "__main__":
	asyncio.run(main())
