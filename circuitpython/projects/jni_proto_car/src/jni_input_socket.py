import wifi
import jni_wifi
import socketpool
import time
import struct
import errno
import asyncio


class InputSocket:

	PORT = 8080        # Port to listen on

	def __init__(self) -> None:
		self.x_float = 0
		self.y_float = 0

		print("Connecting to wifi...")
		jni_wifi.connect_wifi()
		pool = socketpool.SocketPool(wifi.radio)
		print(f"Opening Input socket at this IP: {wifi.radio.ipv4_address}")
		HOST = str(wifi.radio.ipv4_address)

		server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
		server_socket.bind((HOST, self.PORT))
		server_socket.listen(1)
		self.server_socket = server_socket
		self.client_socket: socketpool.Socket | None = None

	def get_last_input(self) -> tuple[float, float]:
		return self.x_float, self.y_float

	async def loop_async(self, sleep_loops: float = 0):
		while True:
			if self.client_socket is None:
				print("Waiting for a connection...")
				self.client_socket, addr = self.server_socket.accept()
				print('Connected with', addr)	
				self.client_socket.setblocking(False)	
				print('Connected with', addr)
			self.read_from_client()
			await asyncio.sleep(sleep_loops)

	def read_from_client(self) -> None:
		continue_pulling = True
		# packets_pulled = 0
		while continue_pulling:
			try:
				message = bytearray(2)
				num_bytes = self.client_socket.recv_into(message)
				if num_bytes > 0:
					# packets_pulled += 1
					x, y = struct.unpack("<bb", message)
					if x == 99 and y == 99:
						print("Received end command!")
						self.client_socket.close()
						print("Client socket closed.")
						self.client_socket = None
					else:
						self.x_float = x / 100
						self.y_float = y / 100
						print(f"Received: {self.x_float}, {self.y_float}")
				else:
					continue_pulling = False
			except OSError as err:
				if errno.EAGAIN == err.args[0]:
					...
					continue_pulling = False
					# No data available to read
				else:
					self.client_socket.close()
					self.client_socket = None
					print(f"Error with client sockert: {err}")
		# print(f"Received {packets_pulled} packets from client.")
