import socket
import struct
import asyncio
import time

SERVER_IP = '192.168.199.201'
#  SERVER_IP = '192.168.199.121'
#  SERVER_IP = '192.168.199.245'
# SERVER_IP = '192.168.199.233'
SERVER_PORT = 8080
# LOOP_TIME_BUDGET = 1  # 1 Hz
#  LOOP_TIME_BUDGET = 0.1  # 10 Hz
LOOP_TIME_BUDGET = 0.01  # 100 Hz

TIME_TO_LOOP = 5

packets_sent = 0


def send_to_server(udp_socket: socket.socket, x: int, y: int) -> None:
	message = struct.pack('<hh', x, y)  # Little endian, two bytes
	print(f"Sending: {x}, {y}")
	udp_socket.send(message)
	global packets_sent 
	packets_sent += 1


async def loop_with_server(udp_socket: socket.socket) -> None:
	start_timestamp = time.monotonic()
	keep_running = True
	
	x_counter = -100
	y_counter = 100

	while keep_running:
		loop_start_timestamp = time.monotonic()
		if loop_start_timestamp - start_timestamp > TIME_TO_LOOP:
			keep_running = False
			print(f"Sending end command after {TIME_TO_LOOP} seconds")
			send_to_server(udp_socket, 99, 99)
			print(f"Sent {packets_sent} packets")
		else:
			x_counter += 1
			if x_counter > 100:
				x_counter = -100
			y_counter -= 1
			if y_counter < -100:
				y_counter = 100
			x = x_counter
			y = y_counter
			send_to_server(udp_socket, x, y)

		now = time.monotonic()
		timepassed = now - loop_start_timestamp
		time_left = LOOP_TIME_BUDGET - timepassed
		if time_left > 0:
			await asyncio.sleep(time_left)
		

async def main() -> None:
	# Create a UDP socket
	print("Creating socket")
	udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Connect the socket to the server's IP address and port
	server_address = (SERVER_IP, SERVER_PORT)
	print(f"Connecting to {server_address}...")
	udp_socket.connect(server_address)

	await loop_with_server(udp_socket)
	# Close the socket
	udp_socket.close()


if __name__ == "__main__":
	asyncio.run(main())
