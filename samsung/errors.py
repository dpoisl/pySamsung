"""error classes for samsung remote"""


__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"


class AuthenticationError(Exception):
    """app is not authenticated"""
    pass


class ConnectionError(Exception):
    """couldn't connect to device"""
    pass


class TimeoutError(Exception):
    """communication timeout"""
    pass
