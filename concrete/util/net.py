import socket


def find_port():
    '''
    Find and return an available TCP port.

    >>> find_port() > 1023
    True
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr = s.getsockname()
    port = addr[1]
    s.close()
    return port
