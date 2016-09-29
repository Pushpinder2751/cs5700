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

# do it at the end
# username = sys.argv[1]     #USERNAME extracted from input
# pwd = sys.argv[2]     #PASSWORD extracted from input


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



# this is needed for sending HTTP requestes in correct formats
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
    "username="+username+"&password="+pwd+"&csrfmiddlewaretoken="+token[0]+"&next=%2Ffakebook%2F",
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
visited_urls = ['http://david.choffnes.com/', 'http://www.northeastern.edu', 'mailto:choffnes@ccs.neu.edu', 'http://www.ccs.neu.edu/home/choffnes/']
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

# collecting some stats about server behaviours :
count_200 = 0
count_500 = 0
count_301 = 0
count_404 = 0
flag_count = 0
already_visited_links = 0
while urls_to_visit:
    # I am not sure why this happens, but after sometime if socket is not
    # connected again, the reply is garbage. mabe some overflow problem.
    # Ask ta or professor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('cs5700sp16.ccs.neu.edu', 80))
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
    # print r

    soup = BeautifulSoup(r)

    # find flag here:
    # looks something like : <h2 class='secret_flag' style="color:red">FLAG: 64-characters-of-random-alphanumerics</h2>
    # flag_search = soup.find_all('div',class_='secret_flag')

    # flag_search=re.findall(r'FLAG: (\w*)',r, re.I)
    flag_search = soup.findAll('h2', {'class': 'secret_flag'})
    # this is a simple counter to exit the event loop when we collect
    # 5 flags
    if flag_search != []:
        flag_count = flag_count + 1
        if flag_count == 5:
            s.close()
            break
        print flag_count
        print "flag search : ", flag_search





    # this next code will parse all the links carefully
    # and give us the URLs to parse only.
    link_count = 0
    for link in soup.find_all('a'):
        # print(link.get('href'))
        link_count = link_count + 1
        item = link.get('href')

        if item in visited_urls:
            # print "link already visited"
            already_visited_links = already_visited_links + 1
        else:
            # print "adding "+item+" to urls_to_visit"
            urls_to_visit.append(item)
    print "no_of_links on a page : ", link_count

    # important steps :
    # append the current url to visited_urls
    visited_urls.append(urls_to_visit[0])
    urls_to_visit.pop(0)


    if r[0:12] == 'HTTP/1.1 200' :
        count_200 = count_200 + 1
        # add this url to the visited urls
        # visited_urls.append(urls_to_visit[0])
        # # removing this visited url
        # urls_to_visit.pop(0)


    # this means url has been moved, and we have to extract new url from this
    elif r[0:12] == 'HTTP/1.1 301' or r[0:12] == 'HTTP/1.1 302':
        # find moved url here, need to find a way from BeautifulSoup as well as
        # this is not efficient
        urls_to_visit[0]=r.split('\r\n')[5][39:]
        count_301 = count_301 + 1

    elif r[0:12] == 'HTTP/1.1 404' or r[0:12] == 'HTTP/1.1 403':
        count_404 = count_404 + 1
        del urls_to_visit[0]

    elif r[0:12] == 'HTTP/1.1 500':
        count_500 = count_500 + 1
    # to avoid this, I am connecting to socket again and agian!
    else:
        pass
        # no need to do anything here
        # print "something else came up"
        # print r
        # urls_to_visit.pop(0)







# print "new list to visit: : ",urls_to_visit
print "total urls visited : ", len(visited_urls)
print "200 : ", count_200
print "301 or 302: ", count_301
print "403 or 404 : ", count_404
print "500 : ", count_500
print "flag_count : ", flag_count
print "already_visited_links : ", already_visited_links


# def check_validArgs():
#     #checking for validity of arguements
#     if len(sys.argv) > 3 r len(sys.argv) < 3:
#         print "Usage : > ./webcrawler [NEUID] [PASSWORD]"
#         return
