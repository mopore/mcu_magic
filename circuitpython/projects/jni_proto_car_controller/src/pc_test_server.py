import socket
import struct
import errno
import time


def main() -> None:
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
		with client_socket:
			client_socket.setblocking(False)
			print('Connected with', addr)
			keep_client = True
			last_timestamp = time.monotonic()
			message_counter = 0

			while keep_client:
				now = time.monotonic()
				timepassed = now - last_timestamp
				try:
					message = bytearray(2)
					num_bytes = client_socket.recv_into(message)
					if num_bytes > 0:
						message_counter += 1
						x, y = struct.unpack("<bb", message)  # Little endian, two bytes
						if x == 99 and y == 99:
							print("Received end command!")
							keep_client = False
							client_socket.close()
							print("Client socket closed.")
					if timepassed > 1:
						last_timestamp = now	
						print(f"{message_counter} messages/second")
						message_counter = 0
				except OSError as err:
					if errno.EAGAIN == err.args[0]:
						# No data available to read
						time.sleep(.1)
					else:
						keep_client = False
						client_socket.close()
						print(f"Error with client sockert: {err}")


if __name__ == "__main__":
	main()
