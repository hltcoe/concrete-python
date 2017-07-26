from __future__ import unicode_literals
import socket


def find_port():
    '''
    Find and return an available TCP port.

    Returns:
        an unused TCP port (an integer)
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    addr = s.getsockname()
    port = addr[1]
    s.close()
    return port
