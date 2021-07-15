import socket
import dhcppython


# create UDP socket for client
def create_udp_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return client


# create discovery message with mac_address by dhcppython library
def create_discovery_message(mac_address):
    return dhcppython.packet.DHCPPacket.Discover(mac_address)


message = b"give me IP!!!"
# while True:
#     client.sendto(message, ('<broadcast>', 30067))
#     data, addr = client.recvfrom(1024)
#     print("received message: %s"%data)


if __name__ == "__main__":
    client_socket = create_udp_socket()
    client_socket.bind(("", 30068))  # 30068 for client port

    took_ip_from_dhcp = False
    while not took_ip_from_dhcp:
        di

