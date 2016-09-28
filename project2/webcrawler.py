# !/usr/bin/python
# chmod 0744 client2.py
# the above lines give appropriate permissions to run directly
# client.py
import socket
# to parse arguments
import sys, getopt
# to parse Regex
import re
# to parse urls
from urlparse import urlparse


from bs4 import BeautifulSoup

host = 'cs5700f16.ccs.neu.edu'
port = 80

# these values are to be taken from commandline later
username = "001906268"
pwd = "9Z1V07EG"

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
s.connect((host, port))
# message = "GET /accounts/login/ HTTP/1.1\r\n"
# s.send(message)
# not sure how to form this message, saw this in request headers in chrome dev tools
s.send("GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: cs5700sp16.ccs.neu.edu\r\n\r\n")

recieved_msg = s.recv(4096)
print recieved_msg
# we need token and sessionid
token = re.findall(r'csrftoken=(\w+)', recieved_msg,  re.I)
session_id = re.findall(r'sessionid=(\w+)', recieved_msg,  re.I)
print token
print session_id

# will do this later
# soup = BeautifulSoup(recieved_msg)


CRLF = "\r\n"
# this is part of the HTTP format, have to use it after every line

request_post = [
    "POST /accounts/login/ HTTP/1.1",
    "Host: cs5700f16.ccs.neu.edu",
    "Content-Length: 109",
    "Cookie: csrftoken="+token[0]+"; sessionid="+session_id[0],
    "",
    "username=001906268&password=9Z1V07EG&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F",
]




print "does this work???"
print CRLF.join(request_post)
# s.send(p)       #Sent a post request with all parameters


s.send(CRLF.join(request_post))
#over writing old received_msg as it is no longer needed
received_msg = s.recv(4096)
print received_msg

# getting the new seeion_id
new_session_id = re.findall(r'sessionid=(\w+)', recieved_msg,  re.I)
print new_session_id

urls_to_visit = ['/fakebook/']
visited_urls = ['http://david.choffnes.com/', 'http://www.northeastern.edu/', 'mailto:choffnes@ccs.neu.edu']
# print urls_to_visit[0]
# # have to implement bfs here.
# # while urls_to_visit:
#
#
#
# new_GET = [
#     "GET "+urls_to_visit[0]+" HTTP/1.1",
#     "Host: cs5700f16.ccs.neu.edu",
#     "Cookie: csrftoken="+token[0]+"; sessionid="+new_session_id[0],
#     "",
#     "",
#     ]
#
# print CRLF.join(new_GET)
#
# s.send(CRLF.join(new_GET))
# r = s.recv(4096)
# print r
