import socket
import dhcppython

MAC_ADDRESS = "de:ad:be:ef:c0:de"


# create UDP socket for client
def create_udp_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasting mode
    return client


# create discovery message with mac_address by dhcppython library
def create_discovery_message(mac_address):
    return dhcppython.packet.DHCPPacket.Discover(mac_address)


# create request message with mac_address by dhcppython library
def create_request_message(mac_address):
    return dhcppython.packet.DHCPPacket.Request(mac_address)



if __name__ == "__main__":
    client_socket = create_udp_socket()
    client_socket.bind(('', 30068))  # 30068 for client port

    took_ip_from_dhcp = False
    while not took_ip_from_dhcp:
        # create discovery message and send to all DHCP server (broadcast)
        discovery_msg = create_discovery_message(MAC_ADDRESS)
        client_socket.sendto(discovery_msg.asbytes, ('<broadcast>', 30067))
        response_from_DHCP_server, address = client_socket.recvfrom(1024)
        print("received message from DHCP server : ", response_from_DHCP_server)
