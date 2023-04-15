import wifi
import socketpool
import struct
import board
import displayio
import time

import jni_wifi
import adafruit_displayio_sh1107


SERVER_IP = '192.168.199.245'
# SERVER_IP = '192.168.199.233'
SERVER_PORT = 8080
# LOOP_TIME_BUDGET = 1  # 1 Hz
LOOP_TIME_BUDGET = 0.1  # 10 Hz

TIME_TO_LOOP = 5


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


class ClientSocket:

	def __init__(self) -> None:
		self.socket_to_server: socketpool.Socket | None = None

	def connect_to_server(self) -> None:
		home_address = (SERVER_IP, SERVER_PORT)
		print(f"Opening socket to server ({home_address})...")
		pool = socketpool.SocketPool(wifi.radio)
		socket_to_server = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
		socket_to_server.connect(home_address)
		print("Socket to server opened.")
		self.socket_to_server = socket_to_server
	
	def sent_to_server(self, x: int, y: int) -> None:
		if self.socket_to_server is not None:
			message = struct.pack('<bb', x, y)
			print(f"Sending: {x}, {y}")
			self.socket_to_server.send(message)

	def loop_with_server(self, time_budget: float) -> None:	
		start_timestamp = time.monotonic()
		keep_running = True
		
		x_counter = -100
		y_counter = 100

		while keep_running:
			loop_start_timestamp = time.monotonic()
			if loop_start_timestamp - start_timestamp > time_budget:
				keep_running = False
				print(f"Sending end command after {TIME_TO_LOOP} seconds")
				self.sent_to_server(99, 99)
			else:
				x_counter += 1
				if x_counter > 100:
					x_counter = -100
				y_counter -= 1
				if y_counter < -100:
					y_counter = 100
				x = x_counter
				y = y_counter
				self.sent_to_server(x, y)

			now = time.monotonic()
			timepassed = now - loop_start_timestamp
			time_left = LOOP_TIME_BUDGET - timepassed
			ratio = timepassed / LOOP_TIME_BUDGET
			# print(f"Consumption time: {timepassed} ratio: {ratio:.2f}")
			if ratio > 3:
				raise Exception("System has a speed problem!")
			if time_left > 0:
				time.sleep(time_left)


def main() -> None:
	activate_oled_when_present()
	jni_wifi.connect_wifi()
	client_socket = ClientSocket()
	client_socket.connect_to_server()
	client_socket.loop_with_server(TIME_TO_LOOP)


if __name__ == "__main__":
	main()
