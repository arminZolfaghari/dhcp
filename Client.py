import random
import socket
import threading

import dhcppython, ipaddress

MAC_ADDRESS = "de:ad:be:ef:c0:de"
INITIAL_INTERVAL = 10
BACKOFF_CUTOFF = 120
LEASE_TIME = 10
global TOOK_IP_FROM_DHCP, client_socket
TOOK_IP_FROM_DHCP = False


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
def create_request_message(mac_address, xid, offer_ip):
    # return dhcppython.packet.DHCPPacket.Request(mac_address, seconds=0, tx_id=xid, yiaddr=ipaddress.IPv4Address("192.168.1.6"))
    return dhcppython.packet.DHCPPacket(op="BOOTREQUEST", htype="ETHERNET", hlen=6, hops=0, xid=xid, secs=0, flags=0,
                                        ciaddr=ipaddress.IPv4Address(0), yiaddr=ipaddress.IPv4Address(offer_ip),
                                        siaddr=ipaddress.IPv4Address(0), giaddr=ipaddress.IPv4Address(0),
                                        chaddr=mac_address, sname=b'', file=b'', options=dhcppython.options.OptionList(
            [dhcppython.options.options.short_value_to_object(53, "DHCPREQUEST")]))


def client_have_ip():
    global client_socket, number_of_try
    if not TOOK_IP_FROM_DHCP:
        number_of_try += 1
        start_client()
    else:
        print("CLient have ip.")


# this timer starts after send first discovery message
def timer_for_first_discovery_message():
    duration = INITIAL_INTERVAL
    timer_countdown = threading.Timer(duration, client_have_ip, args=None, kwargs=None)
    timer_countdown.start()


def timer_for_second_discovery_message():
    global last_duration
    duration = 2 * (random.random()) * last_duration
    if duration >= BACKOFF_CUTOFF:
        duration = BACKOFF_CUTOFF

    last_duration = duration
    timer_countdown = threading.Timer(duration, client_have_ip, args=None, kwargs=None)
    timer_countdown.start()


# when lease time is finish, returns ip to DHCP
def return_ip_to_dhcp_server():
    global TOOK_IP_FROM_DHCP
    TOOK_IP_FROM_DHCP = False
    print("CLient: Returns ip to DHCP server,"
          "Client don't have ip\n---------------------------------------------")


def timer_for_expire_ip():
    timer_countdown = threading.Timer(LEASE_TIME, return_ip_to_dhcp_server, args=None, kwargs=None)
    timer_countdown.start()


# create discovery message and send to all DHCP server (broadcast)
def send_discovery_message(client_socket):
    discovery_msg = create_discovery_message(MAC_ADDRESS)
    client_socket.sendto(discovery_msg.asbytes, ('localhost', 6667))
    print("Client send discovery message.(broadcast)")

    global number_of_try
    if number_of_try == 1:
        timer_for_first_discovery_message()
    else:
        timer_for_second_discovery_message()


def send_request_message(mac_address, xid, offer_ip):
    global client_socket
    request_msg = create_request_message(mac_address, xid, offer_ip)
    client_socket.sendto(request_msg.asbytes, ('localhost', 6667))
    print("Client send request message to get this ip {} from DHCP server".format(offer_ip))


def start_client():
    global TOOK_IP_FROM_DHCP, client_socket
    while True:
        while not TOOK_IP_FROM_DHCP:

            send_discovery_message(client_socket)
            response_from_DHCP_server, address = client_socket.recvfrom(1024)
            dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(response_from_DHCP_server)
            dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
            if dhcp_message_type == "DHCPOFFER":
                offer_ip = dhcp_packet.yiaddr
                dhcp_message_xid = dhcp_packet.xid
                print("Client get DHCP offer message from DHCP server, offer ip: {}".format(offer_ip))
                send_request_message(MAC_ADDRESS, dhcp_message_xid, offer_ip)

            while True:
                response_from_DHCP_server, address = client_socket.recvfrom(1024)
                dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(response_from_DHCP_server)
                dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
                if dhcp_message_type == "DHCPACK":
                    client_ip = dhcp_packet.yiaddr
                    print("Client get ACK message from DHCP server for this ip : {}".format(client_ip))
                    TOOK_IP_FROM_DHCP = True
                    timer_for_expire_ip()
                    break

                elif dhcp_message_type == "DHCPNACK":
                    print("Client get NACK message from DHCP server!!!")
                    TOOK_IP_FROM_DHCP = False
                    break


if __name__ == "__main__":
    global client_socket
    client_socket = create_udp_socket()
    client_socket.bind(('', 6668))  # 30068 for client port

    global number_of_try, last_duration
    number_of_try = 1
    last_duration = INITIAL_INTERVAL
    start_client()
