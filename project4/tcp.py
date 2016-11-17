# This is the file which creates TCP header and does all the related
# functions.
'''
                        Protocol Layering

                        +---------------------+
                        |     higher-level    |
                        +---------------------+
                        |        TCP          |
                        +---------------------+
                        |  internet protocol  |
                        +---------------------+
                        |communication network|
                        +---------------------+
'''

'''
TCP Header
0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Data |           |U|A|P|R|S|F|                               |
   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
   |       |           |G|K|H|T|N|N|                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Checksum            |         Urgent Pointer        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             data                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
'''


from random import randint
import socket
from struct import *

# custom files
import utility


class TCP_packet:
    def __init__(self, source_ip = '', source_port = 0, dest_ip = '', dest_port = 80, data = ''):
        self.source_port = source_port
        self.dest_port = dest_port
        self.seq_no = 0
        self.ack_no = 0
        self.data_offset = 5 # 4 bit field, size of tcp header, 5 * 4 = 20 bytes

        # there are other bits as well, some are reserved, we will only create
        # the ones we neee to use for the porject
        # total bits : 12 : 3(reserved) + 9(flags aka control bits)
        self.urg = 0 # indicates that the Urgent pointer field is significant
        self.ack = 0 # indicates that the Acknowledgment field is significant.
        #  All packets after the initial SYN packet sent by the client should have this flag set
        self.psh = 0 # Push function. Asks to push the buffered data to the receiving application
        self.rst = 0 # reset the connection
        self.syn = 0 #  Synchronize sequence numbers.
        #  Only the first packet sent from each end should have this flag set.
        self.fin = 0 # No more data from sender
        self.window_size = 4096
        self.check = 0
        self.urgent = 0
        self.data = data
        self.source_ip = source_ip
        self.dest_ip = dest_ip

    def reset(self):
        self.source_port = 0
        self.dest_port = 0
        self.seq_no = 0
        self.ack_no = 0
        self.data_offset = 5 # 4 bit field, size of tcp header, 5 * 4 = 20 bytes

        # there are other bits as well, some are reserved, we will only create
        # the ones we neee to use for the porject
        # total bits : 12 : 3(reserved) + 9(flags aka control bits)
        self.urg = 0 # indicates that the Urgent pointer field is significant
        self.ack = 0 # indicates that the Acknowledgment field is significant.
        #  All packets after the initial SYN packet sent by the client should have this flag set
        self.psh = 0 # Push function. Asks to push the buffered data to the receiving application
        self.rst = 0 # reset the connection
        self.syn = 0 #  Synchronize sequence numbers.
        #  Only the first packet sent from each end should have this flag set.
        self.fin = 0 # No more data from sender
        self.window_size = 4096
        self.check = 0
        self.urgent = 0
        self.data = ''
        self.source_ip = self.source_ip
        self.dest_ip = self.dest_ip

    def construct_tcp_header(self):
        tcp_offset_res = (self.data_offset << 4) + 0
        # we are only going to use these 6 flags in the project
        tcp_flags = self.fin + \
                    (self.syn << 1) + \
                    (self.rst << 2) + \
                    (self.psh << 3) + \
                    (self.ack << 4) + \
                    (self.urg << 5)

        # tcp header without checksum
        tcp_header = pack('!HHLLBBHHH',
                            self.source_port,
                            self.dest_port,
                            self.seq_no,
                            self.ack_no,
                            tcp_offset_res,
                            tcp_flags,
                            self.window_size,
                            self.check,
                            self.urgent)

        # assemble pseudo header first to calculate checksum
        tcp_header_pseudo = pack( '!4s4sBBH',
                                    socket.inet_aton(self.source_ip),
                                    socket.inet_aton(self.dest_ip),
                                    0,
                                    socket.IPPROTO_TCP,
                                    self.data_offset * 4 + len(self.data)  )


        # calculate checksum here
        self.check = utility.checksum(tcp_header_pseudo + tcp_header + self.data)
        # print "checksum calculated  : ", self.check
        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header_1 = pack('!HHLLBBH',
                            self.source_port,
                            self.dest_port,
                            self.seq_no,
                            self.ack_no,
                            tcp_offset_res,
                            tcp_flags,
                            self.window_size) + pack('H' , self.check) + pack('!H' , self.urgent)

        # print tcp_header + self.data
        return tcp_header_1


    def re_construct_tcp_header(self, raw_packet):
        # tcph = unpack('!HHLLBBHHH', raw_packet)
        # print tcph

        # re_construct_tcp_header here
        [self.source_port,
         self.dest_port,
         self.seq_no,
         self.ack_no,
         tcp_offset_res,
         tcp_flags,
         self.window_size] = unpack('!HHLLBBH' , raw_packet[0:16])

        #  unpacking checksum, still confused to if use !H or H here
        [self.check] = unpack('H', raw_packet[16:18])
        [self.urgent] = unpack('!H', raw_packet[18:20])

        # tcp_header length
        self.data_offset = tcp_offset_res >> 4

        # tcp flags
        # just extract that flag and save value by proper offset
        self.fin = tcp_flags & 0x01
        self.syn = (tcp_flags & 0x02) >> 1
        self.rst = (tcp_flags & 0x04) >> 2
        self.psh = (tcp_flags & 0x08) >> 3
        self.ack = (tcp_flags & 0x10) >> 4
        self.urg = (tcp_flags & 0x20) >> 5

        # data
        self.data = raw_packet[self.data_offset * 4:]

        # this is still confusing! as TA and get clarificatoin
        # calculate checksum here :
        # assemble pseudo header first to calculate checksum
        # tcp_header_pseudo = pack( '!4s4sBBH',
        #                             socket.inet_aton(self.source_ip),
        #                             socket.inet_aton(self.dest_ip),
        #                             0,
        #                             socket.IPPROTO_TCP,
        #                             self.data_offset * 4 + len(self.data)  )

        # print utility.checksum(tcp_header_pseudo + raw_packet)


    def print_tcp_header(self):
        print "source_port : ", self.source_port
        print "dest_port : ", self.dest_port
        print "seq_no : ", self.seq_no
        print "ack_no : ", self.ack_no
        # print "tcp_offset_res : ", self.tcp_offset_res
        print "flags : fin : ", self.fin, " syn : ", self.syn, " rst : ", self.rst
        print " psh : ", self.psh, " ack : ", self.ack, " urg : ", self.urg
        print "window size : ", self.window_size
        print "checksum : ", self.check
        print "urgent : ", self.urgent
        print "data offset : ", self.data_offset
        # print "data : "
        # print data
