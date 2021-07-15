import socket
import time


# create UDP socket for DHCP server
def create_udp_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) #UDP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return server


# message = b"this is your IP"
# while True:
#     server.sendto(message, ('<broadcast>', 30068))
#     print("message sent!")
#     time.sleep(1)

if __name__ == "__main__":
    DHCP_server = create_udp_socket()
    DHCP_server.bind(("", 30067))   # 30067 for DHCP server port
    # DHCP_server.settimeout(0.2)
