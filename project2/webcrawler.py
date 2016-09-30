# !/usr/bin/python
# chmod 0744 client2.py
# the above lines give appropriate permissions to run directly
# client.py
import socket
# to parse arguments
import sys, getopt
# to parse Regex
import re
# for BeautifulSoup
import lxml
# for exception
import traceback


from bs4 import BeautifulSoup


host = 'cs5700f16.ccs.neu.edu'
port = 80

# these values are to be taken from commandline later
# username = "001906268"
# pwd = "9Z1V07EG"


def check_validArgs():
    #checking for validity of arguements
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print "Usage : > ./webcrawler [NEUID] [PASSWORD]"
        exit()

check_validArgs()

# do it at the end
username = sys.argv[1]     #USERNAME extracted from input
pwd = sys.argv[2]     #PASSWORD extracted from input


# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect to the server
s.connect((host, port))
# send the raw HTML header
s.send("GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: cs5700f16.ccs.neu.edu\r\n\r\n")

# have caused naming conflicts before
recieved_msg_1 = s.recv(4096)
# print recieved_msg_1

# we need token and sessionid
token = re.findall(r'csrftoken=(\w+)', recieved_msg_1,  re.I)
session_id = re.findall(r'sessionid=(\w+)', recieved_msg_1,  re.I)
# print token
# print session_id



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
# print CRLF.join(request_post)

# send the request over to the server
s.send(CRLF.join(request_post))

# overwriting other variable caused issues, ask more about it to the ta
received_msg_2 = s.recv(4096)
# print received_msg_2

if received_msg_2.find("HTTP/1.1 302 FOUND") == -1:
    print "POST failed! check your credentials again"
    exit()


# getting the new seeion_id
new_session_id = re.findall(r'sessionid=(\w+)', received_msg_2,  re.I)
# print "newSession_id : ",new_session_id


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
count_unexpected_response = 0
count_exceptions_raised = 0
flag_count = 0
already_visited_links = 0
captured_flags = []
stupid_urls = []

# BFS queue
urls_to_visit = ['/fakebook/']
visited_urls = ['http://david.choffnes.com/', 'http://www.northeastern.edu', 'mailto:choffnes@ccs.neu.edu', 'http://www.ccs.neu.edu/home/choffnes/']
# print urls_to_visit[0]


while urls_to_visit:
    if urls_to_visit[0] not in visited_urls:
        # I am not sure why this happens, but after sometime if socket is not
        # connected again, the reply is garbage. mabe some overflow problem.
        # Ask ta or professor
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('cs5700f16.ccs.neu.edu', 80))

        try:
            new_GET = [
            "GET "+urls_to_visit[0]+" HTTP/1.1",
            "Host: cs5700f16.ccs.neu.edu",
            "Cookie: csrftoken="+token[0]+"; sessionid="+new_session_id[0],
            "",
            "",
            ]
            # print CRLF.join(new_GET)
            # send the HTTP GET request to the server
            s.send(CRLF.join(new_GET))
            # receive the incoming data
            r = s.recv(4096)

            # find the flag out of the given page:
            # find flag here:
            # looks something like : <h2 class='secret_flag' style="color:red">FLAG: 64-characters-of-random-alphanumerics</h2>


            soup = BeautifulSoup(r, "lxml") # start BeautifulSoup here

            # can be done in two ways
            # flag_search = soup.findAll('h2', {'class': 'secret_flag'})

            flag_search = re.findall(r'FLAG: (\w*)',r, re.I)

            # this is a simple counter to exit the event loop when we collect
            # 5 flags

            if flag_search != []:
                flag_count = flag_count + 1
                print flag_search[0]
                captured_flags.append(flag_search[0])
                if flag_count == 5:
                    s.close()
                    break
            # print "flag_count", flag_count

            # parse received file here :

            if r[0:12] == 'HTTP/1.1 200':
                count_200 = count_200 + 1
                # BFS code here :
                # append the url to the visited_urls list
                visited_urls.append(urls_to_visit[0])
                # remove the url from the urls_to_visit list
                urls_to_visit.pop(0)

                link_count = 0
                for link in soup.findAll('a', href=True):
                    # keeping count of links parsed
                    link_count = link_count + 1
                    # print(link.get('href'))
                    if link['href'] not in visited_urls:
                        urls_to_visit.append(link['href'])
                    else:
                        # print "link already visited"
                        # count already visited urls seen
                        already_visited_links = already_visited_links + 1

                # print "no_of_links on a page : ", link_count

            elif r[0:12] == 'HTTP/1.1 301' or r[0:12] == 'HTTP/1.1 302':

                visited_urls.append(urls_to_visit[0])
                # no need to do a pop here since we are replacing the url
                # find moved url and replace it with the current one
                urls_to_visit[0]=r.split('\r\n')[5][39:]

                # counting the stats
                count_301 = count_301 + 1

            elif r[0:12] == 'HTTP/1.1 404' or r[0:12] == 'HTTP/1.1 403':
                count_404 = count_404 + 1
                # these urls are not to be visited again
                visited_urls.append(urls_to_visit[0])
                urls_to_visit.pop(0)

            elif r[0:12] == 'HTTP/1.1 500':
                # this is done delebrately by the server, we just have to revisit this link
                count_500 = count_500 + 1
            else:
                count_unexpected_response = count_unexpected_response + 1
                # this case is encountered when we keep sending and receiving on same
                # packet again and again
                # after carefully analysing, sometimes the links are extracted
                # wrong, for eg. GET fakebook/815/ HTTP/1.1,
                # I edit them to /fakebook... and it works

                # print urls_to_visit[0]
                # just to make sure my assumption made above is correct
                stupid_urls.append(urls_to_visit[0])

                urls_to_visit[0] = "/"+urls_to_visit[0]
                # check if the updated url is in visited_urls, otherwise
                # might get the same flag
                if urls_to_visit[0] in visited_urls:
                    urls_to_visit.pop(0)



        except Exception, e:
            # do nothing here : try again
            # usually occurs when BFS fails, has occured in some cases
            # as the server generates random tags
            # professor has not mentioned what to do in this case
            count_exceptions_raised = count_exceptions_raised + 1
            traceback.print_exc()
    else:
        already_visited_links = already_visited_links + 1
        # encountered already visited url
        urls_to_visit.pop(0)




# # Ucomment this to know what server does better
# # Some stats form the crawler
# print captured_flags
# print stupid_urls
# print "total urls visited : ", len(visited_urls)
# print "200 : ", count_200
# print "301 or 302: ", count_301
# print "403 or 404 : ", count_404
# print "500 : ", count_500
# print "unexpected response : ", count_unexpected_response
# print "Exceptions : ", count_exceptions_raised
# print "flag_count : ", flag_count
# print "already_visited_links : ", already_visited_links
