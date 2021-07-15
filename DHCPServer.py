import socket, threading, subprocess
import dhcppython
import time


# create UDP socket for DHCP server
def create_udp_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # enable broadcasting mode
    return server


def create_offer_message():
    pass


# DHCP server must be multi thread
def start_DHCP_server(server):
    server.listen()
    while True:
        connection, address = server.accept()
        print("connection is {} and address is {}".format(connection, address))
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()


def handle_client(connection, address):
    pass


# message = b"this is your IP"
# while True:
#     server.sendto(message, ('<broadcast>', 30068))
#     print("message sent!")
#     time.sleep(1)

if __name__ == "__main__":
    DHCP_server = create_udp_socket()
    DHCP_server.bind(("", 30067))  # 30067 for DHCP server port
    # DHCP_server.settimeout(0.2)

    print(DHCP_server)

    print("*** DHCP server is starting ***")
    start_DHCP_server(DHCP_server)
