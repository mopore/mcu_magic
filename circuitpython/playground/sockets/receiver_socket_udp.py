import wifi
import asyncio
import socketpool
import struct
import board
import displayio
import time
import errno

import jni_wifi
import adafruit_displayio_sh1107


#  LOOP_TIME_BUDGET = 1  # 1 Hz
LOOP_TIME_BUDGET = 0.1  # 10 Hz
CHECK_INTEGRITY = True
# CHECK_INTEGRITY = False

WHITE = 0xFFFFFF
WIDTH = 128
HEIGHT = 64


def activate_oled_when_present() -> displayio.Display | None:
	try:
		displayio.release_displays()
		i2c = board.I2C()
		display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
		display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
		return display
	except Exception:
		# No display found
		return None


class Receiver:
	
	PORT = 8080

	def __init__(self) -> None:
		pool = socketpool.SocketPool(wifi.radio)
		my_ip = wifi.radio.ipv4_address
		print(f"Opening udp socket at this IP: {my_ip}")
		HOST = str(my_ip)
		self._udp_socket = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
		self._udp_socket.setblocking(False)  # type: ignore
		self._udp_socket.bind((HOST, self.PORT))
		self._b = bytearray(4)
		self.keep_running = True
		self._last_x = -101
		self._used_total = 0
		print("UDP socket started.")
	
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
				self._used_total += 1
				print(f"using: {x}, {y} (total: {self._used_total})")

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
			else:
				print(f"Time budget issue: {time_in_loop:.3f} s)")


async def main() -> None:
	# activate_oled_when_present()
	jni_wifi.connect_wifi()
	receiver = Receiver()
	loop_task = asyncio.create_task(receiver.loop_async(LOOP_TIME_BUDGET))
	await asyncio.gather(loop_task)


if __name__ == "__main__":
	asyncio.run(main())
