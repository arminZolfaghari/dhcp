import socket
import dhcppython, ipaddress

MAC_ADDRESS = "de:ad:be:ef:c0:de"
INITIAL_INTERVAL = 10
BACKOFF_CUTOFF = 120


# create UDP socket for client
def create_udp_socket():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasting mode
    return client


# create discovery message with mac_address by dhcppython library
def create_discovery_message(mac_address):
    return dhcppython.packet.DHCPPacket.Discover(mac_address)


# create request message with mac_address by dhcppython library
def create_request_message(mac_address, xid, offer_ip):
    # return dhcppython.packet.DHCPPacket.Request(mac_address, seconds=0, tx_id=xid, yiaddr=ipaddress.IPv4Address("192.168.1.6"))
    return dhcppython.packet.DHCPPacket(op="BOOTREQUEST", htype="ETHERNET", hlen=6, hops=0, xid=xid, secs=0, flags=0,
                                        ciaddr=ipaddress.IPv4Address(0), yiaddr=ipaddress.IPv4Address(offer_ip),
                                        siaddr=ipaddress.IPv4Address(0), giaddr=ipaddress.IPv4Address(0),
                                        chaddr=mac_address, sname=b'', file=b'', options=dhcppython.options.OptionList(
            [dhcppython.options.options.short_value_to_object(53, "DHCPREQUEST")]))


if __name__ == "__main__":
    client_socket = create_udp_socket()
    client_socket.bind(('', 6668))  # 30068 for client port

    took_ip_from_dhcp = False
    while not took_ip_from_dhcp:
        # create discovery message and send to all DHCP server (broadcast)
        discovery_msg = create_discovery_message(MAC_ADDRESS)
        client_socket.sendto(discovery_msg.asbytes, ('localhost', 6667))
        print("Client send discovery message.(broadcast)")
        response_from_DHCP_server, address = client_socket.recvfrom(1024)
        dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(response_from_DHCP_server)
        dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
        if dhcp_message_type == "DHCPOFFER":
            offer_ip = dhcp_packet.yiaddr
            dhcp_message_xid = dhcp_packet.xid
            print("Client get DHCP offer message from DHCP server, offer ip: {}".format(offer_ip))
            request_msg = create_request_message(MAC_ADDRESS, dhcp_message_xid, offer_ip)
            client_socket.sendto(request_msg.asbytes, ('localhost', 6667))
            print("Client send request message to get this ip {} from DHCP server".format(offer_ip))

        while True:
            response_from_DHCP_server, address = client_socket.recvfrom(1024)
            dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(response_from_DHCP_server)
            dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
            if dhcp_message_type == "DHCPACK":
                client_ip = dhcp_packet.yiaddr
                print("Client get ACK message from DHCP server for this ip : {}".format(client_ip))
                break

            elif dhcp_message_type == "DHCPNACK":
                print("Client get NACK message from DHCP server!!!")
                break
