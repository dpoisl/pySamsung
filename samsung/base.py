"""base functionality for samsung remote control"""

__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("lenbytes", "lenstr", "lenstr64", "Connection", "Message")


from base64 import b64encode
import socket

from . import errors


LOCAL_MAC = "00:23:4d:b3:a2:cd" #TODO: get from interface?


def lenbytes(string):
    """Return the length of a string as byte string"""
    length = len(string)
    if length > 256 * 256:
        raise ValueError("String too long")
    return chr(length % 256) + chr(length / 256)


def lenstr(string):
    """
    convert a string to samsungs string format
    
    samsung strings contain the length as integer, a 0 byte and then
    the original string
    """
    return "%s%s" % (lenbytes(string), string)


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
    return src[2:length+2]


class Message(object):
    """
    A message sent by a samsung device

    Instance attributes:
    type -- message type
    payload -- message payload
    sender -- name of the sending device
    """
    # message types
    TYPE_KEY_CONFIRM = 0x00 # key happened in tv mode
    TYPE_STATE_CHANGE = 0x02 # seems to be a status update from TV!
    TYPE_KEY_IN_MENU = 0x01 # key happened in menu or other modes?
    
    # data content: authentication request
    AUTH_OK = "\x64\x00\x01\x00"
    AUTH_ACCESS_DENIED = "\x64\x00\x00\x00"
    #TODO: if AUTH_NEED_CONFIRM, will OK or denied be sent later?
    AUTH_NEED_CONFIRM = "\x0a\x00\x02\x00\x00\x00" 
    AUTH_TIMEOUT = "\x64\x00"

    KEY_OK = "\x00\x00\x00\x00" # reponse from key press (always 0x00000000?)
    
    
    STATUS_SHOWING_MENU = '\n\x00\x02\x00\x00\x00' #TODO: ?
    STATUS_SHOWING_TV = '\n\x00\x01\x00\x00\x00' #TODO: ?

    def __init__(self, data):
        """
        constructor
        
        parse a message from a samsung device

        data -- binary data the device sent
        """
        self.type = ord(data[0])
        self.sender = parse_lenstr(data[1:])
        self.payload = parse_lenstr(data[len(self.sender) + 3:])
        self._raw_data = data

    def __repr__(self):
        """textual representation"""
        return "<Message from=%s, type=%x, data=%r>" % (
                self.sender, self.type, self.payload)

    
    def __eq__(self, other):
        """compare for equality"""
        if isinstance(other, basestring):
            return self.__eq__(Message(other))
        elif isinstance(other, Message):
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
        self.host = host
        self.port = port
        self.app_label = app_label
        self._local_host = None
        self._sock = None
        self._local_mac = None
        self.auth_timeout = auth_timeout
        self.recv_timeout = recv_timeout
        super(Connection, self).__init__()

    def connect(self, auth_timeout=20.0, recv_timeout=2.0):
        """connect to the device"""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(auth_timeout)
        try:
            self._sock.connect((self.host, self.port))
        except socket.error:
            raise errors.ConnectionError("Couldn't connect to %s:%d" % (
                self.host, self.port))
        self._local_host = self._sock.getsockname()[0]
        self._local_mac = LOCAL_MAC

        auth_content = "\x64\x00%s%s%s" % (lenstr64(self._local_host),
                                           lenstr64(self._local_mac),
                                           lenstr64(self.app_label))
        auth = "\x00%s%s" % (lenstr(self.app_label + ".iapp.samsung"), 
                             lenstr(auth_content))
        try:
            self._sock.send(auth)
            ar = self._sock.recv(2048)
            auth_response = Message(ar)
        except socket.timeout:
            raise errors.TimeoutError("Timeout in authentication")
        
        if auth_response.payload == Message.AUTH_OK:
            self._sock.settimeout(recv_timeout)
            return True
        elif auth_response.payload == Message.AUTH_ACCESS_DENIED:
            self._sock.close()
            raise errors.AuthenticationError("access denied by remote device")
        elif auth_response.payload == Message.AUTH_NEED_CONFIRM:
            raise errors.AuthenticationError("please allow this remote on your device")
        elif auth_response.payload == Message.AUTH_TIMEOUT:
            raise errors.AuthenticationError("timeout")
        else:
            print("unknown result: %r" % auth_response)
    
    def disconnect(self):
        self._sock.close()
        self._sock = None
    
    def recv(self):
        try:
            d = self._sock.recv(2048)
        except socket.error:
            raise
        except socket.timeout:
            return None
        else:
            return d

    def _send(self, data):
        if self._sock is None:
            self.connect(self.auth_timeout, self.recv_timeout)
        try:
            return self._sock.send(data)
        except socket.timeout:
            raise errors.TimeoutError("failed to send data")
        except socket.error:
            raise errors.ConnectionError("failed to send data")
