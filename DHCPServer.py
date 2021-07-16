import random
import socket, threading, subprocess
import dhcppython, ipaddress
import json
import time

# global parameters
MACADDRESS_IP_DICT = {}
IP_POOL = []
BLACK_LIST_MACADDRESS = []
RESERVATION_LIST_MAC_IP = {}
LEASE_TIME = 0
MAC_ADDRESS = "de:a0:be:ef:c0:de"


# read config.json
def read_from_config_file():
    file = open('config.json')
    data = json.load(file)
    return data


# create ip pool when pool_mode is 'range'
def create_ip_pool_range(from_ip, to_ip):
    ip_pool_arr = []
    from_ip_parts = from_ip.split('.')
    to_ip_parts = to_ip.split('.')
    for i in range(int(from_ip_parts[3]), int(to_ip_parts[3]) + 1):
        ip = from_ip_parts[0] + "." + from_ip_parts[1] + "." + from_ip_parts[2] + "." + str(i)
        ip_pool_arr.append(ipaddress.IPv4Address(ip))

    return ip_pool_arr


# convert subnet to ip
subnet_to_ip_convertor = {
    "252": {"start": "1", "end": "2"},
    "248": {"start": "1", "end": "6"},
    "240": {"start": "1", "end": "14"},
    "224": {"start": "1", "end": "30"},
    "192": {"start": "1", "end": "62"},
    "124": {"start": "1", "end": "126"},
    "0": {"start": "1", "end": "254"},
}


# create ip pool when pool_mode is 'range'
def create_ip_pool_subnet(ip_block, subnet_mask):
    ip_pool_arr = []
    subnet_mask_parts = subnet_mask.split('.')
    ip_block_parts = ip_block.split('.')
    start_end_host_id = subnet_to_ip_convertor[subnet_mask_parts[3]]
    for i in range(int(start_end_host_id["start"]), int(start_end_host_id["end"]) + 1):
        ip = ip_block_parts[0] + "." + ip_block_parts[1] + "." + ip_block_parts[2] + "." + str(i)
        ip_pool_arr.append(ipaddress.IPv4Address(ip))

    return ip_pool_arr


# ip in reservation list, never should assign to another client
def check_ip_pool_with_reservation_ip(reservation_list, ip_pool):
    for mac, ip in reservation_list.items():
        ip_address = ipaddress.IPv4Address(ip)
        if ip_address in ip_pool:
            ip_pool.remove(ip_address)


# set DHCP server setting
def extract_server_config():
    config = read_from_config_file()
    pool_mode = config["pool_mode"]
    ip_pool_arr = []
    if pool_mode == "range":
        from_ip = config["range"]["from"]
        to_ip = config["range"]["to"]
        ip_pool_arr = create_ip_pool_range(from_ip, to_ip)

    elif pool_mode == "subnet":
        ip_block = config["subnet"]["ip_block"]
        subnet_mask = config["subnet"]["subnet_mask"]
        ip_pool_arr = create_ip_pool_subnet(ip_block, subnet_mask)

    global LEASE_TIME, BLACK_LIST_MACADDRESS, RESERVATION_LIST_MAC_IP, IP_POOL
    LEASE_TIME = config["lease_time"]
    RESERVATION_LIST_MAC_IP = config["reservation_list"]
    BLACK_LIST_MACADDRESS = config["black_list"]
    IP_POOL = ip_pool_arr

    check_ip_pool_with_reservation_ip(RESERVATION_LIST_MAC_IP, IP_POOL)


# create UDP socket for DHCP server
def create_udp_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasting mode
    return server


# select ip from pool and give offer to client
def select_ip_from_pool():
    print(IP_POOL)
    if len(IP_POOL) > 0:
        selected_ip = random.choice(IP_POOL)
        # x.pop(random.randrange(len(x)))
        return selected_ip


def create_offer_message(mac_address, xid, client_mac_address):
    offer_ip = select_ip_from_pool()
    if client_mac_address in MACADDRESS_IP_DICT:
        offer_ip = MACADDRESS_IP_DICT[client_mac_address]

    print("DHCP Server get offer ip to client : ", offer_ip)
    return dhcppython.packet.DHCPPacket.Offer(mac_address, seconds=0, tx_id=xid, yiaddr=offer_ip)


def create_ack_message(mac_address, xid, allocated_ip):
    return dhcppython.packet.DHCPPacket(op="BOOTREPLY", htype="ETHERNET", hlen=6, hops=0, xid=xid, secs=0, flags=0,
                                        ciaddr=ipaddress.IPv4Address(0), yiaddr=ipaddress.IPv4Address(allocated_ip),
                                        siaddr=ipaddress.IPv4Address(0), giaddr=ipaddress.IPv4Address(0),
                                        chaddr=mac_address, sname=b'', file=b'', options=dhcppython.options.OptionList(
            [dhcppython.options.options.short_value_to_object(53, "DHCPACK")]))


def create_nack_message(mac_address, xid):
    return dhcppython.packet.DHCPPacket(op="BOOTREPLY", htype="ETHERNET", hlen=6, hops=0, xid=xid, secs=0, flags=0,
                                        ciaddr=ipaddress.IPv4Address(0), yiaddr=ipaddress.IPv4Address(0),
                                        siaddr=ipaddress.IPv4Address(0), giaddr=ipaddress.IPv4Address(0),
                                        chaddr=mac_address, sname=b'', file=b'', options=dhcppython.options.OptionList(
            [dhcppython.options.options.short_value_to_object(53, "DHCPNACK")]))


def check_client_ip_request(client_mac_address, requested_ip):
    global IP_POOL, MACADDRESS_IP_DICT
    if requested_ip in IP_POOL:
        IP_POOL.remove(requested_ip)
        MACADDRESS_IP_DICT[client_mac_address] = requested_ip
        return True

    elif MACADDRESS_IP_DICT[client_mac_address] == requested_ip:
        return True

    else:
        return False


def is_client_in_black_list(client_mac_address):
    if client_mac_address in BLACK_LIST_MACADDRESS:
        return True

    return False


def return_ip_to_pool(client_mac_address):
    returned_ip = MACADDRESS_IP_DICT[client_mac_address]
    del MACADDRESS_IP_DICT[client_mac_address]
    IP_POOL.append(returned_ip)
    print("return this ip: {} from this client: {} to ip pool".format(returned_ip, client_mac_address))
    print("NEW IP POOL : ", IP_POOL)


# after lease time, returns ip to ip_pool
def timer_for_lease_time(client_mac_address):
    timer_countdown = threading.Timer(LEASE_TIME, return_ip_to_pool, args=[client_mac_address], kwargs=None)
    timer_countdown.start()


# after get DHCP discovery, send DHCP offer
def send_offer_message(server, xid, client_mac_address):
    print("DHCP Server get discover message from client")
    offer_msg = create_offer_message(MAC_ADDRESS, xid, client_mac_address)
    server.sendto(offer_msg.asbytes, ('<broadcast>', 6668))


def handle_client(server, data, client_address, socket_lock):
    dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(data)
    client_mac_address = dhcp_packet.chaddr
    if is_client_in_black_list(client_mac_address):
        print("DHCP Server: this client in blacklist!!!")
        return

    dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
    dhcp_message_xid = dhcp_packet.xid

    if dhcp_message_type == "DHCPDISCOVER":
        send_offer_message(server, dhcp_message_xid, client_mac_address)


    elif dhcp_message_type == "DHCPREQUEST":
        client_mac_address = dhcp_packet.chaddr
        requested_ip = dhcp_packet.yiaddr
        print("DHCP Server get request message from client.(requested ip : {})".format(requested_ip))
        allocate_ip_flag = check_client_ip_request(dhcp_packet.chaddr, requested_ip)
        if allocate_ip_flag:
            ack_msg = create_ack_message(MAC_ADDRESS, dhcp_message_xid, requested_ip)
            print("DHCP Server send ACK to client.(ip {})"
                  "\n----------------------------------------------------------".format(requested_ip))
            server.sendto(ack_msg.asbytes, ('<broadcast>', 6668))
            timer_for_lease_time(client_mac_address)

        else:
            nack_msg = create_nack_message(MAC_ADDRESS, dhcp_message_xid)
            print("DHCP Server send NACK to client.(ip {})".format(requested_ip))
            server.sendto(nack_msg.asbytes, ('<broadcast>', 6668))


# wait for clients and handle their requests
def wait_for_clients(server, socket_lock):
    while True:
        # receive request from client
        data_from_client, client_address = server.recvfrom(10000)
        handle_client(server, data_from_client, client_address, socket_lock)
        # if data_from_client:
        #     thread = threading.Thread(target=handle_client,
        #                               args=(server, data_from_client, client_address, socket_lock))
        #     thread.setDaemon(True)
        #     thread.start()


# DHCP server must be multi thread
def start_DHCP_server(server):
    extract_server_config()
    # socket_lock = threading.Lock()
    socket_lock = 2
    wait_for_clients(server, socket_lock)
    # server.listen()
    # while True:
    #     data_from_client, address = server.recvfrom(1024)
    #     print("connection is {} and address is {}".format(data_from_client, address))
    #     dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(data_from_client)
    #     # print(dhcp_packet)
    #     if dhcp_packet.op == "BOOTREQUEST" and
    #     thread = threading.Thread(target=handle_client, args=(data_from_client, address))
    #     thread.start()


# message = b"this is your IP"
# while True:
#     server.sendto(message, ('<broadcast>', 30068))
#     print("message sent!")
#     time.sleep(1)

if __name__ == "__main__":
    DHCP_server = create_udp_socket()
    DHCP_server.bind(('localhost', 6667))  # 30067 for DHCP server port
    # DHCP_server.settimeout(0.2)

    print(DHCP_server)
    print("*** DHCP server is starting ***")
    start_DHCP_server(DHCP_server)
