import random
import getopt
import socket
from struct import *
import struct
import sys

import SocketServer
import threading


# custom files :
import measurements
"""
DNS Header
0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5  6
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                       ID                      |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR| Opcode |AA|TC|RD|RA|    Z   |     RCODE    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
DNS Query
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
/                      QNAME                    /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      QTYPE                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      QCLASS                   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
DNS Answer
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
/                       NAME                    /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                       TYPE                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      CLASS                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                       TTL                     |
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     RDLENGTH                  |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
/                      RDATA                    /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
"""

"""
Important links to understand DNS :
http://www.networksorcery.com/enp/protocol/dns.htm

https://www.ietf.org/rfc/rfc1035.txt
"""

# we will create sevral classes : DNS_packet, DNS_query, DNS_ans

class DNS_Packet:
    def __init__(self):
        self.id = random.randint(0, 65535)
        self.flags = 0
        self.qcount = 0
        self.account = 0
        self.nscount = 0
        self.arcount = 0
        self.query = DNS_query()
        self.answer = DNS_answer()


    def construct_dns_packet_query(self, domain_name):
        self.account = 1
        self.flags = 0x8180

        packet = pack("!HHHHHH", self.id, self.flags,
                              self.qcount, self.account,
                              self.nscount, self.arcount)
        # self.query.qclass = 0
        # packet += self.query.construct_dns_query( self.query.qname )
        packet += self.query.data
        return packet

# this will be used quite often as this is the main job of our DNS
    def construct_dns_answer(self, domain_name, ip):
        # have to know why these values get to be like this :
        self.answer = DNS_answer()

        packet = self.construct_dns_packet_query(domain_name)
        # print self.answer.print_DNS_answer()
        # print "ip address : ", ip
        packet += self.answer.construct_DNS_answer_2(ip)
        # print "qclass : ", packet
        return packet



    def re_construct_dns_packet(self, raw_packet):
        [self.id,
        self.flags,
        self.qcount,
        self.account,
        self.nscount,
        self.arcount] = unpack("!HHHHHH", raw_packet[:12])
        self.query = DNS_query()
        self.query.re_construct_dns_query(raw_packet[12:])
        # self.query.re_construct_dns_query_2(raw_packet[12:])
        self.answer = None # this is something we will create
        # print struct.unpack('!H', raw_packet[0:2])
        # print self.id

    def print_DNS_packet(self):
        print "DNS_Packet : "
        print "id : ", self.id
        print "flags : ", self.flags
        print "qcount : ", self.qcount
        print "account : ", self.account
        print "nscount : ", self.nscount
        print "arcount : ", self.arcount
        print "query : "
        self.query.print_DNS_query()
        # self.answer.print_DNS_answer()
        # print "answer : "
        # self.answer.print_DNS_answer

"""
DNS QUESTION Format
 0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 												|
| 					 QNAME 						|
| 												|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|					 QTYPE 						|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 					 QCLASS 					|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
"""


class DNS_query:
    def __init__(self):
        self.qname = ''
        self.qtype = 1
        self.qclass = 0
        self.data = ''

    def re_construct_dns_query(self, raw_data):
        self.data = raw_data
        [self.qtype,
        self.qclass] = unpack('>HH', raw_data[-4:])
        self.qtype = 1
        # print "this is : ", self.qtype, " class : ", self.qclass
        qname = raw_data[:-4]
        # print "qname : ", qname

        # To convert name from DNS to regular format
        # Example : 3www6google3com0 -> www.google.com
        length = 0
        index = 0
        name = []
        # something wrong here : dig sometimes does not give the correct format
        while True:
            # print "index : ", index
            # print qname
            length = ord(qname[index])
            if length > 50:
                length = 9
                name.append(qname[index:index+length])
                index += length
                continue
            # print "length : ", length
            if length == 0:
                break
            index += 1
            name.append(qname[index:index+length])
            index += length
            # print name
        self.qname = '.'.join(name)
        # print "I am here : "
        # print self.qname

    def re_construct_dns_query_2(self, raw_data):
        print raw_data
        length = -1
        index = 0
        name = []
        while length != 0:
            length = ord(raw_data[index])
            if length == 99:
                length = 9
                part = raw_data[index:index+length]
                name.append(part)
                index += length
                continue
            # print length
            index += 1
            part = raw_data[index:index+length]
            name.append(part)
            index += length
        self.data = raw_data
        self.qtype = unpack("!H",raw_data[index:index+2])[0]
        self.qclass = unpack("!H", raw_data[index+2:index+4])[0]
        self.qname = '.'.join(name)
        print self.qname

    def construct_dns_query(self, domain_name):
        # self.qname = domain_name
        # print "1.domanin_name, : ", domain_name
        # print "domain_name : ", self.qname
        dns_query = ''.join(chr(len(x)) + x for x in domain_name.split('.'))
        # where does this come from? the end symbol
        dns_query += '\x00'
        print "dns_query = ", dns_query
        print "qclass : ", self.qclass
        packet = dns_query + pack('!HH', self.qtype, self.qclass)
        print packet
        return packet




    def print_DNS_query(self):
        print "DNS_query : "
        print "qtype : ", self.qtype
        print "qclass : ", self.qclass
        print "qname : ", self.qname


class DNS_answer():
    def __init__(self):
        self.aname = 0
        self.atype = 0
        self.aclass = 0
        self.ttl = 0
        self.data = ''
        self.len = 0

    def construct_DNS_answer_2(self, ip):
        self.aname = 0xc00c
        self.atype = 0x0001
        self.aclass = 0x0001
        self.ttl = 40
        self.data = ip
        self.len = 4
        DNS_answer = pack('>HHHLH4s', self.aname, self.atype, self.aclass,
                                  self.ttl, self.len, socket.inet_aton(self.data))

        return DNS_answer

    # I don't think I need this

    def print_DNS_answer(self):
        print "DNS_answer : "
        print "aname : ", self.aname
        print "atype : ", self.atype
        print "aclass : ", self.aclass
        print "ttl : ", self.ttl
        print "data : ", self.data
        print "length : ", self.len

# this dictionary saves all the client to server mappings so that we do not have
# calculate them again and again
client_mappings = {}

# this is the request handler, it's job is :
# 1. reassemble the DNS packet
# 2. from the query, calculate a response if not already cached
# 3. assemble a DNS response packet and send it back to client

class My_DNS_UDP_Handler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        # print data
        # print struct.unpack('!H', data[0:2])
        socket = self.request[1]
        dns_packet = DNS_Packet()
        dns_packet.re_construct_dns_packet(data)
        # print dns_packet.query.qname
        # print "client IP : ", self.client_address[0]
        if self.client_address[0] not in client_mappings:
            # print "clinet mappings : ", client_mappings


            # check if the ip given is private! as we are not able to use
            # geo ip on it
            # private ip is a very rare case
            if measurements.private_ip(self.client_address[0]):
                # print "private ip sent by client : "
                data = dns_packet.construct_dns_answer(dns_packet.query.qname, '54.210.1.206')
                client_mappings[self.client_address[0]] = '54.210.1.206'
                socket.sendto(data, self.client_address)
            else:
                # print "calculating ans ip "
                # dns_packet.print_DNS_packet()
                # have to make a response here :
                x = measurements.get_geo_from_ip(self.client_address[0])
                # change it from unicode to float for calculations
                geo_location_client_address = [float(x[0]), float(x[1])]
                # print "client_geo : ", geo_location_client_address
                answer_ip = measurements.least_distant_server(geo_location_client_address)

                domain_name = dns_packet.query.qname
                client_mappings[self.client_address[0]] = answer_ip
                # print "domain_name : ", domain_name
                data = dns_packet.construct_dns_answer(domain_name, answer_ip)
                # print "ans : ", data
                # dns_packet2 = DNS_Packet()
                # dns_packet.re_construct_dns_packet(data)
                # dns_packet.print_DNS_packet()
                socket.sendto(data, self.client_address)
        else:
            # print client_mappings
            # print "responding from cache"
            data = dns_packet.construct_dns_answer(dns_packet.query.qname, client_mappings[self.client_address[0]])
            socket.sendto(data, self.client_address)
        # sys.exit()

# might need it later, for now
# I do not understand why we do not need to bind a UDP server with an ip address
def get_source_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("ccs.neu.edu", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass
ip = '127.0.0.1'
IP = ''
# print "IP : ", IP
port = 42751
cdn_name = 'cs5700cdn.example.com'
name = ''
def parse_input(arg):
    opts, args = getopt.getopt(arg[1:], 'p:n:')

    for opt, arg in opts:
        if opt in ('-p'):
            port = int(arg)
        elif opt in ('-n'):
            name = arg
            if name != cdn_name:
                sys.exit("Wrong cdn name")
        else:
            sys.exit("Syntax : ./dnsserver -p <port> -n <name>")

    return port, name

[port, name] = parse_input(sys.argv)
# print port
# print name
# sys.exit()

# Resource for this implimentation :
# http://www.lampdev.org/programming/python/python-udp-server-python-implementation-tutorial.html

if __name__ == "__main__":
    # print "i am in : "
    # server = SocketServer.UDPServer((IP, port), My_DNS_UDP_Handler)
    # server.serve_forever()
    server = ThreadedUDPServer((IP, port), My_DNS_UDP_Handler)

    ip, port = server.server_address
    server.serve_forever()
    # start a thread with the server --
       # that thread will then start one
       # more thread for each request
    server_thread = threading.Thread(target = server.serve_forever)

    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    # Do I need to do this?
    # server.shutdown()
    # server.server_close()
