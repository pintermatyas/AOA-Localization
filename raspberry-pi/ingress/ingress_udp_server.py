import socket

INGRESS_SERVER_IP = '127.0.0.1'
INGRESS_SERVER_PORT = 9901

server_address = (INGRESS_SERVER_IP, INGRESS_SERVER_PORT)

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the server address
udp_socket.bind(server_address)

print(f"Ingress UDP server listening on {server_address[0]}:{server_address[1]}")

try:
    while True:
        # Receive data from the client
        data, client_address = udp_socket.recvfrom(1024)  # 1024 is the buffer size

        # Process the received data (you can replace this with your own logic)
        print(f"Received data from {client_address}: {data.decode('utf-8')}")

except KeyboardInterrupt:
    print("Ingress UDP server stopped.")
finally:
    udp_socket.close()
