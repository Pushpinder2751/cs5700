import time
import hashlib

start = time.clock()
m = hashlib.md5()
m.update("random string")
name = m.hexdigest() + ".cashed"
print "time taken : ", (time.clock() - start)


hit = {}
start = time.clock()
hit["random string"] = 1
print "time in this : ", (time.clock() - start)
