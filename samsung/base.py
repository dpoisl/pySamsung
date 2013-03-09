"""base functionality for samsung remote control"""

__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("lenstr", "lenstr64", "SmartTV", "Response", "parse_lenstr")


from base64 import b64encode
import socket
import uuid

_logger = None
_mac = "%012x" % uuid.getnode()
LOCAL_MAC = ":".join(_mac[i:i + 2] for i in range(0, 12, 2))


def set_debug(active=True, basename="samsung.base"):
    """
    activate debug messages
    
    sets the global _logger either to None if active is false
    or to a logging.Logger instance with the given name. This
    enables or disables logging of debug messages.

    arguments:
    active -- boolean, set logging on or off
    basename -- string, name for logger instance
    """
    global _logger
    if active:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(basename)
    else:
        _logger = None
    return _logger

def _debug(*args, **kwargs):
    """
    print a debug message
    
    if logging is activated via set_debug the given message will
    be logged via _logger, else nothing happens.

    usage: see logging.Logger.debug(*args)
    """
    if _logger:
        _logger.debug(*args, **kwargs)


def lenstr(string):
    """
    convert a string to samsungs string format
    
    samsung strings contain the length as integer, a 0 byte and then
    the original string
    
    arguments:
    string -- string or unicode instance
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

    arguments:
    src -- bytes or string

    Returns the parsed lenstr and the remaining data
    """
    length = ord(src[0]) + ord(src[1]) * 256
    data = src[2:length + 2]
    if len(data) < length:
        raise ValueError("missing %d bytes in %r" % (length, src))
    return (src[2:length + 2], src[length+2:])


class AuthenticationError(Exception):
    """app is not authenticated"""
    pass


class ConnectionError(socket.error):
    """couldn't connect to device"""
    pass


class TimeoutError(socket.timeout):
    """communication timeout"""
    pass


class DisconnectedError(socket.timeout):
    """we got thrown out"""
    pass


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
    TYPE_KEY_CONFIRM_MENU = 0x01 # key happened in menu or other modes?
    TYPE_TIMESHIFT = 0x04 # something with time shift?
    TYPES_KEY_ACCEPTED = (TYPE_KEY_CONFIRM, TYPE_KEY_CONFIRM_MENU)

    # data content: authentication request
    AUTH_OK = "\x64\x00\x01\x00" # success
    AUTH_ACCESS_DENIED = "\x64\x00\x00\x00" # denied
    #TODO: if AUTH_NEED_CONFIRM, will OK or denied be sent later?
    AUTH_NEED_CONFIRM = "\x0a\x00\x02\x00\x00\x00" # need confirmation
    AUTH_TIMEOUT = "\x64\x00" # timeout

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
    
    def __str__(self):
        """string representation"""
        return "%x:%r" % (self.type, self.payload)

    def __ne__(self, other):
        return not self.__eq__(other)


class SmartTV(object):
    """
    connector for samsung SmartTV devices

    provides basic functionality like authentication, receiving and
    sending data. as well as higher level functionality like sending
    key codes or strings (eG for text input fields).
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
        self._auth_tries = 3

    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r)" % (self.__class__.__name__, 
                                           self.app_label, self._sockargs[0],
                                           self._sockargs[1], self.auth_timeout,
                                           self.recv_timeout)
    
    def connect(self):
        """connect to device and authenticate"""
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
        """authenticate with samsung device"""
        socket_name = self._sock.getsockname()[0]
        auth_content = "\x64\x00%s%s%s" % (lenstr64(socket_name),
                                           lenstr64(LOCAL_MAC),
                                           lenstr64(self.app_label))
        auth = "\x00%s%s" % (lenstr(self.app_label + ".iapp.samsung"), 
                             lenstr(auth_content))
        
        _debug("-> %r", auth)
        self._sock.send(auth)
        status = None

        for i in range(self._auth_tries):
            try:
                _debug("AUTH2 WAIT")
                response = self.recv()
                _debug("AUTH2 Response: %r" % response)
            except socket.timeout:
                self._sock.close()
                self._sock = None
                continue
            else:
                status = self._parse_auth_response(response)
                _debug("2nd AUTH RESPONSE: %r", status)
        if status:
            _debug("OK")
            self._sock.settimeout(self.recv_timeout)
            return True
        else:
            _debug("ERROR")
            raise AuthenticationError("access denied by remote device")

    def _parse_auth_response(self, response):
        """
        parse authentication response
    
        arguments:
        response -- authentication response as string

        Returns None if no response was received or the applicatoin
        should wait, True if the autentication was successfull and False 
        if it failed.
        """
        if response is None:
            _debug("got no response")
            return None
        parsed = Response(response)
        if parsed.payload == Response.AUTH_OK:
            _debug("Authentication successfull")
            return True
        elif parsed.payload == Response.AUTH_ACCESS_DENIED:
            _debug("Authentication response: Access Denied")
            self._sock.close()
            return False
        elif parsed.payload == Response.AUTH_NEED_CONFIRM:
            _debug("Authentication response: waiting for confirmation on device")
            return None
        elif parsed.payload == Response.AUTH_TIMEOUT:
            _debug("Authentication response: Timeout")
            raise AuthenticationError("timeout")
        else:
            _debug("Unknown authentication response")
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
                raise TimeoutError("we got thrown out?")
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
            self.connect()
        try:
            _debug("-> %r", data)
            return self._sock.send(data)
        except socket.timeout:
            raise TimeoutError("failed to send data")
        except socket.error:
            raise ConnectionError("failed to send data")
    
    def send_key(self, key):
        """
        send a key event to the device

        arguments:
        key -- key code to send, must start with "KEY_"
        """
        msg = self._build_message(mode="\x00", 
                                  payload="\x00\x00\x00%s" % lenstr64(key))
        return self.send(msg)

    def send_text(self, text):
        """
        send a text to the device

        texts can only be sent if specific fields are highlighted in the user 
        interface, eG password and user name fields, search fields, etc.

        arguments:
        text -- text to send
        """
        msg = self._build_message(mode="\x01", 
                                  payload="\x01\x00%s" % lenstr64(text))
        return self.send(msg)
    
    def _build_message(self, mode, payload):
        """internal helper - build a message"""
        return "%s%s%s" % (mode, lenstr(self.app_label + ".iapp.samsung"),
                           lenstr(payload))

    def set_channel(self, channel):
        """
        switch to a specific channel

        the given channel is padded to 4 digits and theseare sent to the device
        as single key presses.

        arguments:
        channel -- channel to switch to (0 .. 9999)
        """
        map_ = dict((x, "KEY_%d" % x) for x in range(10))
        for digit in "%04d" % channel:
            self.send_key(map_[digit])
