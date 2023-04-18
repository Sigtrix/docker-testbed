import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1_ip = "10.0.3.4"
client_socket.connect((s1_ip, 12345))
client_socket.send("Hello there, s1!".encode())

response = client_socket.recv(1024).decode()
print(response)

client_socket.close()
