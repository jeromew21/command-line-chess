import socket

def decode(string):
    return string.decode('utf-8')

def encode(string):
    return bytes(string, 'utf-8')

def connectSocket(addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    return s

def bindSocket(addr, port, inc):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    s.listen(inc)
    return s

def closeSocket(s):
    s.close()

def accept(s):
    return s.accept()
    
def waitForMessage(s):
    return decode(s.recv(1024))

def sendMessage(s, message, addr=None):
    message = encode(message)
    if addr:
        s.sendto(message, addr)
    else:
        s.send(message)

def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res