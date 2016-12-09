import urllib
import math
import json
from struct import *
from socket import AF_INET, inet_pton

# I am using Haversine Formula


def get_geo_from_ip(ip):
    url = 'http://ipinfo.io/'+str(ip)+'/json'
    response = urllib.urlopen(url).read()
    # print response
    # need to do parse the data as json
    parsed_resp = json.loads(response)
    # print parsed_resp
    location =  parsed_resp['loc'].split(',')
    return location
# ip = '129.10.9.71'
# print get_geo_from_ip(ip)

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    # returns answer kms
    return d

# print distance(1, 2)
# for now I am hard coding the ip to its geo position
# however I feel there has to be a better way to do this.
# origin : 54.167.4.20
ec2_server_ips = {'54.210.1.206': [39.0481,-77.4728], # N.Virginia
                  '54.67.25.76': [37.3388,-121.8914], # N. California
                  '35.161.203.105': [45.8696,-119.6880], # Oregon
                  '52.213.13.179': [53.3389, -6.2595], # Ireland
                  '52.196.161.198': [35.6427, 139.7677], # Tokyo
                  '54.255.148.115': [1.2855, 103.8565], # Singapore
                  '13.54.30.86': [-33.8612, 151.1982], # Sydney
                  '52.67.177.90': [-23.5464,-46.6289], # Sao Paolo
                  '35.156.54.135': [50.1167, 8.6833] # Franfurt
                  }

# returning the server address with least distance from the client
def least_distant_server(client_geo):
    client = [client_geo]
    # print "client_geo : ", client_geo
    # some temp variables to get the correct values
    distance_to_servers_dict = {}
    for key in ec2_server_ips:
        # print "server geo : ", ec2_server_ips[key]
        distance_to_servers_dict[key] = distance(client_geo , ec2_server_ips[key])

    nearest_server = min(distance_to_servers_dict, key = distance_to_servers_dict.get)
    # print nearest_server
    return nearest_server

# we check if the ip sent by the client is a private ip address
# and then we need to serve it with any random CDN, need to ask professor
# for a better way to handle this.
def private_ip(ip):
    f = unpack('!I', inet_pton(AF_INET, ip))[0]
    # print f
    private = (
        [ 2130706432, 4278190080 ], # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
        [ 3232235520, 4294901760 ], # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
        [ 2886729728, 4293918720 ], # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
        [ 167772160,  4278190080 ], # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
    )
    for net in private:
        # print (f & net[1])
        if (f & net[1]) == net[0]:
            return True
    return False

# print private_ip("10.110.80.132")
