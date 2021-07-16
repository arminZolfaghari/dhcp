import socket
import threading
import dhcppython


class UDPServerMultiClient():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket_lock = threading.Lock()

    # return DHCP pocket ...
    def function(self, params):
        pass

    def handle_client(self, data, client_address):
        params = dhcppython.packet.DHCPPacket.from_bytes(data)
        resp = self.function(params)

        with self.socket_lock:
            self.sock.sendto(resp, client_address)
        print('\n', resp, '\n')

    def wait_for_client(self):
        while True:  # keep alive

            try:  # receive request from client
                data, client_address = self.sock.recvfrom(1024)

                thread = threading.Thread(target=self.handle_client,
                                          args=(data, client_address))
                thread.daemon = True
                thread.start()

            except OSError as err:
                print(err)


def start_server():
    udp_server_multi_client = UDPServerMultiClient('192.168.1.33', 6667)
    # server config TODO
    udp_server_multi_client.wait_for_client()


if __name__ == '__main__':
    start_server()
