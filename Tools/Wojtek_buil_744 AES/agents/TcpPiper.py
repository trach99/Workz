# v0.9
# python

import socket

def onCommand(s):
    soc = socket.socket()
    soc.connect(('localhost', 6789))
    soc.send(s + '\n')
    soc.close()
    return "ok"


def onReset(s):
    soc = socket.socket()
    soc.connect(('localhost', 6789))
    soc.send(s + '\n')
    soc.close()
    return "ok"
