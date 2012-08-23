"""base functionality for samsung remote control"""

__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("lenstr", "lenstr64", "Connection", "Response", 
           "parse_lenstr")


from base64 import b64encode
import socket
import uuid

from . import errors

_logger = None
_mac = "%012x" % uuid.getnode()
LOCAL_MAC = ":".join(_mac[i:i + 2] for i in range(0, 12, 2))


def set_debug(active=True, basename="samsung.base"):
    """activate debug messages"""
    global _logger
    if active:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(basename)
    else:
        _logger = None


def _debug(*args):
    """print a debug message"""
    if _logger:
        _logger.debug(*args)


def lenstr(string):
    """
    convert a string to samsungs string format
    
    samsung strings contain the length as integer, a 0 byte and then
    the original string
    """
    length = len(string)
    if length > 256 * 256:
        raise ValueError("String too long")
    return chr(length % 256) + chr(length / 256) + string


def lenstr64(string):
    """Shortcut: base64 encode a string and create a lenstr of it"""
    return lenstr(b64encode(string))


def parse_lenstr(src):
    """
    parse a string as returned by samsung devices

    Samsung devices send strings with the length as the first two bytes 
    (little endian). This function can be used to get the content from
    these strings.
    """
    length = ord(src[0]) + ord(src[1]) * 256
    data = src[2:length + 2]
    if len(data) < length:
        raise ValueError("missing %d bytes in %r" % (length, src))
    return (src[2:length + 2], src[length+2:])


class Response(object):
    """
    A message sent by a samsung device

    Instance attributes:
    type -- message type
    payload -- message payload
    sender -- name of the sending device
    """
    # message types
    TYPE_KEY_CONFIRM = 0x00 # key happened in tv mode
    TYPE_STATE_CHANGE = 0x02 # status update from TV
    TYPE_KEY_IN_MENU = 0x01 # key happened in menu or other modes?
    TYPE_TIMESHIFT = 0x04 # something with time shift?

    # data content: authentication request
    AUTH_OK = "\x64\x00\x01\x00"
    AUTH_ACCESS_DENIED = "\x64\x00\x00\x00"
    #TODO: if AUTH_NEED_CONFIRM, will OK or denied be sent later?
    AUTH_NEED_CONFIRM = "\x0a\x00\x02\x00\x00\x00" 
    AUTH_TIMEOUT = "\x64\x00"

    KEY_OK = "\x00\x00\x00\x00" # reponse from key press (always 0x00000000?)
    
    STATUS_SHOWING_MENU = '\x10\x00\x02\x00\x00\x00'
    STATUS_SHOWING_TV = '\x10\x00\x01\x00\x00\x00'
    STATUS_SHOWING_TTX = '\x10\x00\x0c\x00\x00\x00'
    STATUS_SHOWING_OVERLAY = '\x10\x00\x18\x00\x00\x00'

    def __init__(self, data):
        """
        constructor
        
        parse a message from a samsung device
        
        arguments:
        data -- binary data the device sent
        """
        self.type = ord(data[0])
        (self.sender, remaining) = parse_lenstr(data[1:])
        (self.payload, remaining) = parse_lenstr(remaining)
        self._raw_data = data
        if len(remaining):
            raise ValueError("Parser error: message %r, remaining data: %r" % (
                             data, remaining))

    def __repr__(self):
        """textual representation"""
        return "<Response from=%s, type=%x, data=%r>" % (
                self.sender, self.type, self.payload)
    
    def __eq__(self, other):
        """compare for equality"""
        if isinstance(other, basestring):
            return self.__eq__(Response(other))
        elif isinstance(other, Response):
            return self.type == other.type and self.payload == other.payload
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(self, other)


class Connection(object):
    """
    connector for samsung devices

    provides basic functionality like authentication, receiving and
    sending data.
    """
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0, 
            recv_timeout=2.0):
        """
        create a new connection

        arguments:
        app_label -- application label to use for authentication and
                     data transmission
        host -- ip address or hostname of the device
        port -- tcp port for remote control connection (default: 55000)
        auth_timeout -- authentication timeout in seconds (default: 20.0, 
                        None=wait forever)
        recv_timeout -- timeout for message polling in seconds. (default: 2.0,
                        None = no timeout)
        """
        self._sockargs = (host, port)
        self.app_label = app_label
        self._sock = None
        self.auth_timeout = auth_timeout
        self.recv_timeout = recv_timeout
        super(Connection, self).__init__()

    def connect(self, auth_timeout=20.0, recv_timeout=2.0):
        self._connect()
        self._authenticate()
    
    def _connect(self):
        """connect to the device"""
        _debug("Connecting to %s:%d", self._sockargs[0], 
                     self._sockargs[1])
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self.auth_timeout)
        try:
            self._sock.connect(self._sockargs)
        except socket.error:
            raise

    def _authenticate(self):
        socket_name = self._sock.getsockname()[0]
        auth_content = "\x64\x00%s%s%s" % (lenstr64(socket_name),
                                           lenstr64(LOCAL_MAC),
                                           lenstr64(self.app_label))
        auth = "\x00%s%s" % (lenstr(self.app_label + ".iapp.samsung"), 
                             lenstr(auth_content))
        
        _debug("-> %r", auth)
        self._sock.send(auth)
        response = self.recv()
        _debug("AUTH1 Response: %r" % response)
        status = self._parse_auth_response(response)
    
        if status is None:
            try:
                _debug("AUTH2 WAIT")
                response = self.recv()
                _debug("AUTH2 Response: %r" % response)
            except socket.timeout:
                self._sock.close()
                self._sock = None
                raise errors.AuthenticationError("timeout in authentication")
            else:
                status = self._parse_auth_response(response)
                _debug("2nd AUTH RESPONSE: %r", status)

        if status:
            _debug("OK")
            self._sock.settimeout(self.recv_timeout)
            return True
        else:
            _debug("ERROR")
            raise errors.AuthenticationError("access denied by remote device")

    def _parse_auth_response(self, response):
        """
        parse authentication response
    
        arguments:
        response -- authentication response as string

        Returns None if no response was received, True if the autentication
        was successfull and False if it failed.
        """
        if response is None:
            _debug("got no response")
            return None
        parsed = Response(response)
        if parsed.payload == Response.AUTH_OK:
            _debug("Message is OK")
            return True
        elif parsed.payload == Response.AUTH_ACCESS_DENIED:
            _debug("Message is 'access denied'")
            self._sock.close()
            return False
        elif parsed.payload == Response.AUTH_NEED_CONFIRM:
            _debug("Message is 'need confirmation'")
            return None
        elif parsed.payload == Response.AUTH_TIMEOUT:
            _debug("Message is 'timeout'")
            raise errors.AuthenticationError("timeout")
        else:
            _debug("message is unknown")
            raise ValueError("unknown auth response: %r" % parsed)

    def disconnect(self):
        """disconnect socket"""
        self._sock.close()
        self._sock = None
    
    def recv(self):
        """recieve data"""
        try:
            data = self._sock.recv(2048)
            if len(data) == 0:
                raise errors.TimeoutError("we got thrown out?")
            _debug("<- %r  (timeout: %r", data, self._sock.gettimeout())
            return data
        except socket.error:
            raise
        except socket.timeout:
            return None

    def send(self, data):
        """
        send raw data to remote device

        if the connection to the remote device is not established,
        self.connect is called before sending th data.

        data -- binary data to send
        """
        if self._sock is None:
            _debug("need to connect first")
            self.connect(self.auth_timeout, self.recv_timeout)
        try:
            _debug("-> %r", data)
            return self._sock.send(data)
        except socket.timeout:
            raise errors.TimeoutError("failed to send data")
        except socket.error:
            raise errors.ConnectionError("failed to send data")
