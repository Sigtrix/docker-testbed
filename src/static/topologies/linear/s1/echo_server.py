import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 12345))
server_socket.listen(1)

while True:
	client_socket, address = server_socket.accept()
	data = client_socket.recv(1024).decode()
	print(f"Received data from {address}: {data}")
	client_socket.send(data.encode())
	client_socket.close()
