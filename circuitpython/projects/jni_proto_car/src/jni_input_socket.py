import wifi
import jni_wifi
import socketpool
import time
import struct
import errno


def main() -> None:
	print("Connecting to wifi...")
	jni_wifi.connect_wifi()
	pool = socketpool.SocketPool(wifi.radio)
	print(f"My address: {wifi.radio.ipv4_address}")

	HOST = str(wifi.radio.ipv4_address)
	PORT = 80        # Port to listen on
	sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
	sock.bind((HOST, PORT))
	sock.listen(1)
	while True:
		print("Waiting for a connection...")
		client_socket, addr = sock.accept()
		with client_socket:
			client_socket.setblocking(False)
			print('Connected with', addr)
			keep_client = True
			# Receive and print data from the client
			while keep_client:
				try:
					message = bytearray(4)
					num_bytes = client_socket.recv_into(message)
					if num_bytes > 0:
						x, y = struct.unpack(">hh", message)
						if x == 999 and y == 999:
							print("Received end command!")
							keep_client = False
							client_socket.close()
							print("Client socket closed.")
						else:
							print(f"Received x:{x}, y:{y}")
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
