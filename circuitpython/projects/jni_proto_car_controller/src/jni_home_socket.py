import wifi
import asyncio
import socketpool
import jni_global_settings as settings
import struct


class HomeSocket:

	def __init__(self) -> None:
		self.keep_running = True
		self.x: float = 0
		self.y: float = 0
		self.init_client_socket()

	def init_client_socket(self) -> None:
		home_address = (settings.HOME_SOCKET_IP, settings.HOME_SOCKET_PORT)  # type: ignore
		print(f"Opening socket to home ({home_address})...")
		pool = socketpool.SocketPool(wifi.radio)
		self.client_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
		print(dir(self.client_socket))
		self.client_socket.connect(home_address)
		print("Socket to home opened.")

	def inform_joy_move(self, x: int, y: int) -> None:
		self.x = x
		self.y = y
	
	def inform_joy_button_a(self, pressed: bool) -> None:
		print(f"inform_joy_button_a: {pressed}")

	def inform_joy_button_b(self, pressed: bool) -> None:
		print(f"inform_joy_button_b: {pressed}")

	def inform_joy_button_x(self, pressed: bool) -> None:
		print(f"inform_joy_button_x: {pressed}")

	def inform_joy_button_y(self, pressed: bool) -> None:
		print(f"inform_joy_button_y: {pressed}")

	async def loop_async(self, loop_sleeps: float = .1):	
		while self.keep_running:
			message = struct.pack('<bb', self.x, self.y)
			self.client_socket.send(message)
			print("Sent message to home.")
			await asyncio.sleep(loop_sleeps)
