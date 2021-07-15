import socket, threading, subprocess
import dhcppython
import json
import time


MACADDRESS_IP_DICT = {}
IP_POOL = []


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
    print(from_ip_parts)
    for i in range(int(from_ip_parts[3]), int(to_ip_parts[3]) + 1):
        ip = from_ip_parts[0] + "." + from_ip_parts[1] + "." + from_ip_parts[2] + "." + str(i)
        ip_pool_arr.append(ip)

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
        ip_pool_arr.append(ip)

    return ip_pool_arr


def extract_server_config():
    config = read_from_config_file()
    pool_mode = config["pool_mode"]
    if pool_mode == "range":
        from_ip = config["range"]["from"]
        to_ip = config["range"]["to"]
        ip_pool_arr = create_ip_pool_range(from_ip, to_ip)
    elif pool_mode == "subnet":
        ip_block = config["subnet"]["ip_block"]
        subnet_mask = config["subnet"]["subnet_mask"]
        ip_pool_arr = create_ip_pool_subnet(ip_block, subnet_mask)

    lease_time = config["lease_time"]
    reservation_list = config["reservation_list"]
    black_list = config["black_list"]
    # TODO: check reservation_list and black_list in ip pool

    return ip_pool_arr, lease_time, reservation_list, black_list


# create UDP socket for DHCP server
def create_udp_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasting mode
    return server


def create_offer_message(mac_address):
    return


def handle_client(data, client_address):
    dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(data)
    dhcp_message_type = dhcp_packet.options.as_dict()["dhcp_message_type"]
    if dhcp_message_type == "DHCPDISCOVER":
        print("DHCP Server get discover message from client")

    print()



# wait for clients and handle their requests
def wait_for_clients(server):
    while True:
        try:  # receive request from client
            data_from_client, client_address = server.recvfrom(1024)
            print("connection is {} and address is {}".format(data_from_client, client_address))
            # dhcp_packet = dhcppython.packet.DHCPPacket.from_bytes(data_from_client)
            # # print(dhcp_packet)
            thread = threading.Thread(target=handle_client, args=(data_from_client, client_address))
            thread.start()

        except OSError as err:
            print(err)


# DHCP server must be multi thread
def start_DHCP_server(server):
    wait_for_clients(server)
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
    DHCP_server.bind(('192.168.1.33', 30067))  # 30067 for DHCP server port
    # DHCP_server.settimeout(0.2)

    print(DHCP_server)
    print("*** DHCP server is starting ***")
    start_DHCP_server(DHCP_server)
