import socket
import struct

# SERVER_IP = '192.168.199.245'
SERVER_IP = '192.168.199.121'
SERVER_PORT = 8080


def main() -> None:
	# Create a TCP/IP socket
	print("Creating socket")
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the server's IP address and port
	server_address = (SERVER_IP, SERVER_PORT)
	print(f"Connecting to {server_address}...")
	client_socket.connect(server_address)

	# Send data to the server
	while True:
		# Read two integers from the user
		x = int(input('Enter the first integer: '))
		y = int(input('Enter the second integer: '))

		# Send the integers to the server
		message = struct.pack('>hh', x, y)

		client_socket.send(message)
		print(f"Sent {message}")
		if x == 999 and y == 999:
			break

	# Close the socket
	client_socket.close()


if __name__ == "__main__":
	main()
