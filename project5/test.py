index = 0
name = []
qname = '3www6google3com0'
while True:
    print ord(qname[index])
    l = ord(qname[index])
    if l == 0:
        break
    index += 1
    name.append(qname[index:index+l])
    index += l
ans = '.'.join(name)
print ans
