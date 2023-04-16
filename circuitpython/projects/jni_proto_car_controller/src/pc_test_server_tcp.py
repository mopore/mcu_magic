import socket
import struct
import errno
import time
import asyncio

# LOOP_TIME_BUDGET = 1  # 1 Hz
LOOP_TIME_BUDGET = 0.1  # 10 Hz
CHECK_INTEGRITY = True
# CHECK_INTEGRITY = False
TIME_TO_LOOP = 5


def read_from_client(client_socket: socket.socket, b: bytearray) -> None | tuple[int, int]:
	""" Return None if no data is available, otherwise return a tuple of two integers. """
	try:
		num_of_bytes = client_socket.recv_into(b)
		if num_of_bytes > 0:
			x, y = struct.unpack("<hh", b)  # Little endian, two bytes
			return x, y
	except OSError as err:
		if errno.EAGAIN == err.args[0]:
			return None
		else:
			client_socket.close()
			print(f"Error with client sockert: {err}")
			raise err


def check_integrity(last_x: int, new_x: int) -> None:
	if new_x == -100:
		return
	if new_x <= last_x:
		raise Exception(f"Integrity problem: {last_x} >= {new_x}")	


def read_client_empty(client_socket: socket.socket, b: bytearray) -> None | tuple[int, int]:
	response: None | tuple[int, int] = None
	last_result = read_from_client(client_socket, b)	
	if last_result is not None:
		response = last_result

	while last_result is not None:
		result = read_from_client(client_socket, b)
		if result is not None:
			x, y = result
			print(f"Loosing: {x}, {y}")
			response = last_result
		else:
			x, y = last_result
			print(f"using: {x}, {y}")
			last_result = None
	return response


async def loop_with_client(client_socket: socket.socket, addr: socket.AddressInfo) -> None:
	client__start_timestamp = time.monotonic()
	used_packages = 0
	expected_packages = TIME_TO_LOOP / LOOP_TIME_BUDGET
	with client_socket:
		client_socket.setblocking(False)
		print('Connected with', addr)
		keep_client = True

		b = bytearray(4)
		while keep_client:
			loop_start_timestamp = time.monotonic()
			last_x = -101
			try:
				result = read_client_empty(client_socket, b)
				if result is not None:
					x, y = result
					if x == 99 and y == 99:
						keep_client = False
					else:
						used_packages += 1
						if CHECK_INTEGRITY:
							check_integrity(last_x, x)
							last_x = x
						
			except OSError as err:
				print(f"Error with client sockert: {err}")
				keep_client = False
			now = time.monotonic()
			timepassed = now - loop_start_timestamp
			time_left = LOOP_TIME_BUDGET - timepassed
			# ratio = timepassed / LOOP_TIME_BUDGET
			client_time = now - client__start_timestamp
			if client_time > TIME_TO_LOOP + 1:
				keep_client = False
			# if ratio > 3:
			# 	raise Exception("System has a speed problem!")
			# if time_left > 0:
				# await asyncio.sleep(time_left)

	print("Client connection end.")	
	lost_ratio = ((expected_packages - used_packages) / expected_packages) * 100
	if lost_ratio < 0:
		lost_ratio = 0

	print(f"Lost packages: {lost_ratio:.0f}%")
	client_socket.close()


async def main() -> None:
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Set the socket option to allow reuse of the address
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# Bind the socket to the address and port
	host = '0.0.0.0'  # Listen on all available interfaces
	port = 8080
	server_socket.bind((host, port))
	server_socket.listen(1)
	while True:
		print("Waiting for a connection...")
		client_socket, addr = server_socket.accept()
		await loop_with_client(client_socket, addr)


if __name__ == "__main__":
	asyncio.run(main())
