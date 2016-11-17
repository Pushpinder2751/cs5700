
# This file just deals with IP header. It's jobs is to construct ip header
# and do all the associated functions



# Ip header RFC 791
# 0                   1                   2                   3
#     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |Version|  IHL  |Type of Service|          Total Length         |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |         Identification        |Flags|      Fragment Offset    |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |  Time to Live |    Protocol   |         Header Checksum       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                       Source Address                          |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                    Destination Address                        |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                    Options                    |    Padding    |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# IP header struct in C, needed for packing and unpacking

# struct ipheader {
#  unsigned char ip_hl:4, ip_v:4; /* this means that each member is 4 bits */
#  unsigned char ip_tos;
#  unsigned short int ip_len;
#  unsigned short int ip_id;
#  unsigned short int ip_off;
#  unsigned char ip_ttl;
#  unsigned char ip_p;
#  unsigned short int ip_sum;
#  unsigned int ip_src;
#  unsigned int ip_dst;
# };

from random import randint
import socket
from struct import *
import utility



class IP_packet:
    def __init__(self, source_ip = '', dest_ip = '', data = ''):
        self.ver = 4
        self.ihl = 5
        self.tos = 0
        self.tot_len = 20
        self.id = 54321
        self.frag_off = 0
        self.ttl = 255
        self.proto = socket.IPPROTO_TCP
        self.check = 0    # kernel will fill the correct checksum
        self.saddr = source_ip
        self.daddr = dest_ip
        self.data = ''
        # self.ip_ihl_ver = (self.ver << 4) + self.ihl

    def reset(self):
        self.ver = 4
        self.ihl = 5
        self.tos = 0
        self.tot_len = 20
        self.id = 54321
        self.frag_off = 0
        self.ttl = 255
        self.proto = socket.IPPROTO_TCP
        self.check = 0    # kernel will fill the correct checksum
        self.saddr = ''
        self.daddr = ''
        self.data = ''
        # self.ip_ihl_ver = (self.ver << 4) + self.ihl

    def construct_ip_header(self):

        # ip header fields
        # self.tot_len = self.ihl * 4 + len(self.data)
        self.id = randint(0, 65535)
        ip_ihl_ver = (self.ver << 4) + self.ihl

        source_addr = socket.inet_aton ( self.saddr )   #Spoof the source ip address if you want to
        dest_addr = socket.inet_aton (self.daddr)
        # the ! in the pack format string means network order
        ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, self.tos, self.tot_len,
        self.id, self.frag_off, self.ttl, self.proto, self.check, source_addr, dest_addr)

        self.check = utility.checksum(ip_header)
        # print "Ip_header checksum construction: ", self.check

        # make the header again with checksum
        ip_header_new = pack('!BBHHHBBH4s4s' , ip_ihl_ver, self.tos, self.tot_len,
        self.id, self.frag_off, self.ttl, self.proto, self.check, source_addr, dest_addr)
        # self.get_ip_header_values(ip_header)
        # print "checksum : ", checksum(ip_header_new)
        # IP packet = ip_header + data
        ip_packet = ip_header_new

        return ip_packet



    def get_ip_header_values(self, ip_header):
        #now unpack them :)
        iph = unpack('!BBHHHBBH4s4s' , ip_header)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF

        iph_length = ihl * 4

        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8]);
        d_addr = socket.inet_ntoa(iph[9]);

        print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)
    # checksum functions needed for calculation checksum

    def re_construct_ip_header(self, raw_packet):
        # print unpack('!BBHHHBB',raw_packet[0:10])
        # self.get_ip_header_values(raw_packet[0:20])
        # extract first 10 bytes of IP_header first
        [version_ihl,
         self.tos,
         self.tot_len,
         self.id,
         self.frag_off,
         self.ttl,
         self.proto] = unpack('!BBHHHBB', raw_packet[0:10])
        # extract checksum here, user 'H' which is unsigned short int = 2 bytes
        # not sure if to use H or !H here
        [self.check] = unpack('H', raw_packet[10:12])
        # extract source and dest ips here, still will need to convert them to ip addresses later
        [source_ip, dest_ip] = unpack('!4s4s', raw_packet[12:20])

        # fill in version and ihl here
        self.ver = version_ihl >> 4
        self.ihl = version_ihl & 0xF
        # print "ihl : ", self.ihl

        # fill in source_ip and dest_ip
        self.saddr = socket.inet_ntoa(source_ip)
        self.daddr = socket.inet_ntoa(dest_ip)

        self.data = raw_packet[self.ihl * 4:self.tot_len]

        header_check = raw_packet[:self.ihl * 4]

        # print "calculated checksum : ", utility.checksum(header_check)
        # print "actual checksum : ", self.check

    def print_ip_header(self):
        print "version : ", self.ver, " ihl : ", self.ihl
        print "tos : ", self.tos
        print "total length : ", self.tot_len
        print "id : ", self.id
        print "frag_off : ", self.frag_off
        print "ttl : ", self.ttl
        print "protocol : ", self.proto
        print "check : ", self.check
        print "source_ip :", self.saddr
        print "destination_ip", self.daddr
