import enum
import ipaddress
import struct


# Extra point

class PacketType(enum.IntEnum):
    BOOTREQUEST = 1
    BOOTREPLY = 2


class PacketFlags(enum.IntEnum):
    BROADCAST = 1 << 15


class HardwareAddressType(enum.IntEnum):
    ETHERNET = 1
    IEEE802 = 6


class MessageType(enum.IntEnum):
    DHCPDISCOVER = 1
    DHCPOFFER = 2
    DHCPREQUEST = 3
    DHCPACK = 5
    DHCPNAK = 6


class Packet(object):
    def __init__(self):
        self.op = None
        self.htype = HardwareAddressType.ETHERNET
        self.hlen = 6
        self.hops = 0
        self.secs = 0
        self.flags = PacketFlags.BROADCAST
        self.xid = None
        self.ciaddr = ipaddress.ip_address('0.0.0.0')
        self.yiaddr = ipaddress.ip_address('0.0.0.0')
        self.siaddr = ipaddress.ip_address('0.0.0.0')
        self.giaddr = ipaddress.ip_address('0.0.0.0')
        self.chaddr = b'\x00\x00\x00\x00\x00\x00'
        self.cookie = b'\x63\x82\x53\x63'
        self.sname = ''
        self.options = []

    def pack(self):
        result = bytearray(bytes(240))
        struct.pack_into('BBBB', result, 0, int(self.op), self.htype, self.hlen, self.hops)
        struct.pack_into('!I', result, 4, self.xid)
        struct.pack_into('!HH', result, 8, self.secs, self.flags)
        struct.pack_into('!II', result, 12, int(self.ciaddr), int(self.yiaddr))
        struct.pack_into('!II', result, 20, int(self.siaddr), int(self.giaddr))
        struct.pack_into('12s', result, 28, self.chaddr)
        struct.pack_into('64s', result, 40, self.sname.encode('ascii'))
        struct.pack_into('4s', result, 236, b'\x63\x82\x53\x63')

        for i in self.options:
            packed = i.pack()
            result += struct.pack('BB{0}s'.format(len(packed)), int(i.id), len(packed), packed)

        result += b'\xff'

        if len(result) < 300:
            result += b'\x00' * (300 - len(result))

        return result
