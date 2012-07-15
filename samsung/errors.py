"""error classes for samsung remote"""


__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"


import socket

class AuthenticationError(Exception):
    """app is not authenticated"""
    pass


class ConnectionError(socket.error):
    """couldn't connect to device"""
    pass


class TimeoutError(socket.timeout):
    """communication timeout"""
    pass
