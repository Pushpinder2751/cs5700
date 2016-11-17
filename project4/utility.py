import socket
import fcntl
import struct


# to get ip address conveinently
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]
# get_ip_address('eth0')  # '192.168.0.110'

# alternate method
# import os
# f = os.popen('ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
# your_ip=f.read()






# we need a new port everytime and we cannot just randomly assign ports as some
# ports are reserved for applications. Hence we assign a port using temp socket
def get_random_port_name():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

# here because it is used in both ip and tcp
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    # print "messageeeeee ---------",msg
    for i in range(0, len(msg), 2):
    	# print "length ---",len(msg)
    	# print i
    	# print i+1
    	# print "msg[i]",msg[i]
    	# print "msg[i+1]",msg[i+1]

        # w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        w = ord(msg[i])
        if i+1<len(msg):
        	w = w+(ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s
