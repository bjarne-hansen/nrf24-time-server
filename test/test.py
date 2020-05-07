import math

future = 0
for now in range(0, 60):

    #future = now + 15

    #if future >= 60:
    #    future = future - 60

    #ft = math.floor(future / 7.5)
    #ft = ft % 7
    #ft = math.ceil(ft / 2.0)
    #ft = ft * 15

    #ft = ft - 1 if ft > 0 else 59

    future = now + 15
    # ft = int(future / 1.0 + 0.5) % 60 * 1
    # ft = int(future / 2.0 + 0.5) % 30 * 2
    # ft = int(future / 5.0 + 0.5) % 12 * 5
    # ft = int(future / 10.0 + 0.5) % 6 * 10
    ft = int(future / 15.0 + 0.5) % 4 * 15
    # ft = int(future / 20.0 + 0.5) % 3 * 20
    #ft = int(future / 30.0 + 0.5) % 2 * 30



    print(now, future, ft)



# protocol: <number>, <description>,
# options: add_timestamp, add_gwid
# id=3s
# reading=H
# vcc=H
# moisture=H
# temperature=h
# humidity=B
#

#
# RD: pn, id, expr => ep
# ID: pn, id, ep, expr => trans
# RA: pn, id, ep, if => mqtt(addr,port, cid, un, pwd)