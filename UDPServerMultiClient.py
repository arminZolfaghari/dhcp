import socket
import threading
import time
from datetime import datetime


# A simple UDP Server for handling multiple clients
class UDPServerMultiClient():

    def __init__(self, host, port):
        super().__init__(host, port)
        self.socket_lock = threading.Lock()

    def handle_request(self, data, client_address):

        # handle request
        name = data.decode('utf-8')
        resp = self.get_phone_no(name)
        self.printwt(f'[ REQUEST from {client_address} ]')
        print('\n', name, '\n')

        # send response to the client
        self.printwt(f'[ RESPONSE to {client_address} ]')
        with self.socket_lock:
            self.sock.sendto(resp.encode('utf-8'), client_address)
        print('\n', resp, '\n')

    def wait_for_client(self):
        ''' Wait for clients and handle their requests '''

        try:
            while True: # keep alive

                try: # receive request from client
                    data, client_address = self.sock.recvfrom(1024)

                    c_thread = threading.Thread(target = self.handle_request,
                                            args = (data, client_address))
                    c_thread.daemon = True
                    c_thread.start()

                except OSError as err:
                    self.printwt(err)

        except KeyboardInterrupt:
            self.shutdown_server()

def main():
    ''' Create a UDP Server and handle multiple clients simultaneously '''

    udp_server_multi_client = UDPServerMultiClient('127.0.0.1', 4444)
    udp_server_multi_client.configure_server()
    udp_server_multi_client.wait_for_client()

if __name__ == '__main__':
    main()