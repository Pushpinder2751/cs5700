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
s.send("GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: cs5700f16.ccs.neu.edu\r\n\r\n")

# have caused naming conflicts before
recieved_msg_1 = s.recv(4096)
print recieved_msg_1
# we need token and sessionid
token = re.findall(r'csrftoken=(\w+)', recieved_msg_1,  re.I)
session_id = re.findall(r'sessionid=(\w+)', recieved_msg_1,  re.I)
print token
print session_id


# will do this later
# soup = BeautifulSoup(recieved_msg)


CRLF = "\r\n"
# this is part of the HTTP format, have to use it after every line

request_post = [
    "POST /accounts/login/ HTTP/1.1",
    "Host: cs5700f16.ccs.neu.edu",
    "Connection: keep-alive",
    "Content-Length: 109",
    "Cache-Control: max-age=0",
    "Referer: http://cs5700f16.ccs.neu.edu/accounts/login/",
    "Cookie: csrftoken="+token[0]+"; sessionid="+session_id[0],
    "",
    "username=001906268&password=9Z1V07EG&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F",
]


# print "does this work???"
# print CRLF.join(request_post)

# send the request over to the server
s.send(CRLF.join(request_post))
# overwriting other variable caused issues, ask more about it to the ta
received_msg_2 = s.recv(4096)
print received_msg_2

# getting the new seeion_id
new_session_id = re.findall(r'sessionid=(\w+)', received_msg_2,  re.I)
print "newSession_id : ",new_session_id

# my queue for BFS
urls_to_visit = ['/fakebook/']
visited_urls = ['http://david.choffnes.com/', 'http://www.northeastern.edu/', 'mailto:choffnes@ccs.neu.edu']
# print urls_to_visit[0]
# have to implement bfs here.

# this get request should look something like this in the end:
# session_start
# GET /fakebook/ HTTP/1.1
# Host: cs5700f16.ccs.neu.edu
# Cookie: csrftoken=8f6f055c3e9142485364242a3544fb29; sessionid=b8be539f2daf57dd3ada613322c18258
#
#
# session end


new_GET = [
    "GET "+urls_to_visit[0]+" HTTP/1.1",
    "Host: cs5700f16.ccs.neu.edu",
    "Cookie: csrftoken="+token[0]+"; sessionid="+new_session_id[0],
    "",
    "",
    ]

# print "start"
# print CRLF.join(new_GET)
# print "end"

s.send(CRLF.join(new_GET))
r = s.recv(4096)
print r

# session_start
# GET /fakebook/ HTTP/1.1
# Host: cs5700f16.ccs.neu.edu
# Cookie: csrftoken=8f6f055c3e9142485364242a3544fb29; sessionid=b8be539f2daf57dd3ada613322c18258
#
#
# session end
