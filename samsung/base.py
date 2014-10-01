"""
base functionality for Samsung remote control
"""

__version__ = "0.2.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("sstv_string", "sstv_base64", "SmartTV", "Message",
           "parse_sstv_string")


import base64
import socket
import logging
import uuid  # used for mac detection
import time

_logger = None
_mac = "%012x" % uuid.getnode()
LOCAL_MAC = ":".join(_mac[i:i + 2] for i in range(0, 12, 2))


class ResponseType(object):
    """
    container for known response types

    this information is extracted from tests with a Samsung UE40D5700 TV set
    and a HT-D5100 BluRay Home Theatre.

    :cvar int KEY_CONFIRM: key received while viewing TV
    :cvar int STATE_CHANGE: status update from SmartTV
    :cvar int KEY_CONFIRM_MENU: key received while in menu
    :cvar int TIMESHIFT: exact meaning unknown, somehow related to time-shift?
    :cvar int TYPES_ACCEPTED: set of all types confirming a received keypress
    """
    KEY_CONFIRM = 0x00
    KEY_CONFIRM_MENU = 0x01
    STATE_CHANGE = 0x02
    TIMESHIFT = 0x04
    TYPES_KEY_ACCEPTED = (KEY_CONFIRM, KEY_CONFIRM_MENU)


class ResponsePayload(object):
    """
    container for known response payloads

    this information is extracted from tests with a Samsung UE40D5700 TV set
    and a HT-D5100 BluRay Home Theatre.

    :cvar str AUTH_OK: authentication response: success
    :cvar str AUTH_ACCESS_DENIED: authentication error: access denied
    :cvar str AUTH_NEED_CONFIRM: authentication response: need confirmation
                                 from user on TV?
    :cvar str AUTH_TIMEOUT: authentication timeout
    :cvar str KEY_OK: response payload for key events
    :cvar str STATUS_SHOWING_MENU: seems to indicate that a menu is active
    :cvar str STATUS_SHOWING_TV: seems to indicate that no menu is visible
    :cvar str STATUS_SHOWING_TTX: seems to indicate that TTX is displayed
    :cvar str STATUS_SHOWING_OVERLAY: sent for some overlays over TV
    """
    AUTH_OK = "\x64\x00\x01\x00"
    AUTH_ACCESS_DENIED = "\x64\x00\x00\x00"
    #TODO: if AUTH_NEED_CONFIRM, will OK or denied be sent later?
    AUTH_NEED_CONFIRM = "\x0a\x00\x02\x00\x00\x00"
    AUTH_TIMEOUT = "\x64\x00"
    KEY_OK = "\x00\x00\x00\x00"

    STATUS_SHOWING_MENU = '\x10\x00\x02\x00\x00\x00'
    STATUS_SHOWING_TV = '\x10\x00\x01\x00\x00\x00'
    STATUS_SHOWING_TTX = '\x10\x00\x0c\x00\x00\x00'
    STATUS_SHOWING_OVERLAY = '\x10\x00\x18\x00\x00\x00'


def set_logging(active=True, logger_name="samsung.base"):
    """
    activate debug messages
    
    sets the global _logger either to None if active is false
    or to a logging.Logger instance with the given name. This
    enables or disables logging of debug messages.

    :param bool active: activate/deactivate logging (default: True)
    :param basestring logger_name: name to use for the logger
    :return: the created logger
    :rtype: logging.Logger or None
    """
    global _logger
    if active:
        logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(logger_name)
    else:
        _logger = None
    return _logger


def _log(level, message, *args, **kwargs):
    """
    handles optional logging (only if set_logging was called with active=True)

    This internally calls logging.Logger.log() with all given arguments if
    a logger is initialized in the modules _logger variable.

    :param level: log level to use
    :param str message: log message to send
    :param args: positional arguments for Logger.log call
    :param kwargs: keyword arguments for Logger.log call
    """
    if _logger:
        return _logger.log(level, message, *args, **kwargs)


def sstv_string(string):
    """
    convert a string to samsungs string format
    
    the samsung communication protocol encodes strings as 2 bytes containing
    the length, then a NULL byte and then the string itself.

    :param str string: text to encode
    :return: the converted string
    :rtype: str
    """
    length = len(string)
    if length > 256 * 256:
        raise ValueError("String too long")
    return chr(length % 256) + chr(length // 256) + string


def sstv_base64(string):
    """
    Shortcut: base64 encode a string and create a sstv_string of it

    :param str string: text to encode
    :return: the resulting sstv_string
    :rtype: str
    """
    return sstv_string(base64.b64encode(string.encode("ASCII")))


def parse_sstv_string(data):
    """
    parse a string as returned by samsung devices

    Samsung devices send strings with the length as the first two bytes 
    (little endian). This function can be used to get the content from
    these strings.

    :param str data: source data
    :return: the parsed string and potentially remaining data
    :rtype: tuple
    """
    _log(logging.DEBUG, "Parsing sstv_string %r", data)
    length = ord(data[0]) + ord(data[1]) * 256
    if len(data) < length + 2:
        raise ValueError("missing %d bytes in %r" % (length, data))
    _log(logging.DEBUG, "Length %d, payload %r, remainder %r",
         length, data[2:length + 2], data[length + 2:])
    return data[2:length + 2], data[length + 2:]


class AuthenticationError(Exception):
    """app is not authenticated"""
    pass


class Message(object):
    """
    A message sent by a samsung device

    :ivar int type: message type
    :ivar str payload: message payload
    :ivar str sender: name of the sending device
    """

    def __init__(self, type_, payload, sender=None):
        """
        constructor

        :param int type_: message type
        :param str payload: message payload
        :param str sender: optional sender indicator
        """
        self.type = type_
        self.payload = payload
        self.sender = sender

    @classmethod
    def parse(cls, message):
        """
        parse a response as received on the network socket

        :param message: payload received on socket
        :return: Message instance with parsed type, payload and sender
        """
        type_ = ord(message[0])
        (sender, remaining) = parse_sstv_string(message[1:])
        (payload, remaining) = parse_sstv_string(remaining)
        if len(remaining):
            raise ValueError("Parser error: message %r, remaining data: %r" % (
                             message, remaining))
        return cls(type_, payload, sender)

    def __repr__(self):
        """textual representation"""
        return "Message(sender=%s, type_=%x, payload=%r)" % (self.sender,
                                                              self.type,
                                                              self.payload)
    
    def __eq__(self, other):
        """
        compare for equality

        :param other: item to compare to
        :type other: str or Message
        :return: equality
        :rtype: bool
        """
        if isinstance(other, str):
            return self.__eq__(Message.parse(other))
        elif isinstance(other, Message):
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

    :ivar str app_label: application name (will be used in authentication)
    """
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0, 
                 recv_timeout=2.0):
        """
        create a new connection

        :param str app_label: application label to use for authentication and
                              data transmission
        :param str host: ip address or hostname of the device
        :param int port: tcp port for remote control connection (default:
                         55000)
        :param float auth_timeout: authentication timeout in seconds (
                                   default: 20.0, None=wait forever)
        :param float recv_timeout: timeout for message polling in seconds. (
                                   default: 2.0, None = no timeout)
        """
        self._sockargs = (host, port)
        self.app_label = app_label
        self._sock = None
        self._auth_timeout = auth_timeout
        self._recv_timeout = recv_timeout
        self._auth_tries = 3

    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r)" % (self.__class__.__name__, 
                                           self.app_label, self._sockargs[0],
                                           self._sockargs[1],
                                           self._auth_timeout,
                                           self._recv_timeout)
    
    def connect(self):
        """connect to device and authenticate"""
        self._connect()
        self._authenticate()
    
    def _connect(self):
        """
        connect to the device

        connects to the device socket

        :raises: socket.error
        """
        _log(logging.DEBUG, "Connecting to %s:%d", self._sockargs[0],
             self._sockargs[1])
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self._auth_timeout)
        try:
            self._sock.connect(self._sockargs)
        except socket.error:
            raise

    def _authenticate(self):
        """
        authenticate with samsung device

        performs authentication with the samsung device and returns the
        authentication result. Raises AuthenticationError if the
        authentication failed.

        :return: True if authentication was successful
        :raises: AuthenticationError, socket.error
        """
        socket_name = self._sock.getsockname()[0]
        auth_content = "\x64\x00%s%s%s" % (sstv_base64(socket_name),
                                           sstv_base64(LOCAL_MAC),
                                           sstv_base64(self.app_label))
        auth = "\x00%s%s" % (sstv_string(self.app_label + ".iapp.samsung"),
                             sstv_string(auth_content))
        _log(logging.DEBUG, "sending %r", auth)
        self._sock.send(auth)
        status = None

        for i in range(self._auth_tries):
            try:
                _log(logging.DEBUG, "AUTH2 WAIT")
                response = self.recv()
                _log(logging.DEBUG, "AUTH2 Response: %r" % response)
            except socket.timeout:
                _log(logging.DEBUG, "AUTH2 timeout")
            else:
                status = self._parse_auth_response(response)
                _log(logging.DEBUG, "2nd AUTH RESPONSE: %r", status)
            if status:
                _log(logging.DEBUG, "OK")
                self._sock.settimeout(self._recv_timeout)
                return True
        else:
            _log(logging.DEBUG, "ERROR")
            raise AuthenticationError("access denied by remote device")

    def _parse_auth_response(self, response):
        """
        parse authentication response

        Parses the response to an authentication request and returns the
        success as boolean. If the device is still waiting for a
        confirmation from the user, None is returned instead.
    
        :param str response: authentication response as string
        :return: None if no response received or we should wait, else
                 authentication result
        :rtype: bool or None
        """
        if response is None:
            _log(logging.DEBUG, "got no response")
            return None
        parsed = Message.parse(response)
        if parsed.payload == ResponsePayload.AUTH_OK:
            _log(logging.DEBUG, "Authentication successful")
            return True
        elif parsed.payload == ResponsePayload.AUTH_ACCESS_DENIED:
            _log(logging.DEBUG, "Authentication response: Access Denied")
            self._sock.close()
            return False
        elif parsed.payload == ResponsePayload.AUTH_NEED_CONFIRM:
            _log(logging.DEBUG, "Authentication response: waiting for "
                 "confirmation on device")
            return None
        elif parsed.payload == ResponsePayload.AUTH_TIMEOUT:
            _log(logging.DEBUG, "Authentication response: Timeout")
            raise AuthenticationError("timeout")
        else:
            _log(logging.DEBUG, "Unknown authentication response")
            raise ValueError("unknown auth response: %r" % parsed)

    def disconnect(self):
        """disconnect socket"""
        self._sock.close()
        self._sock = None
    
    def recv(self):
        """
        receive raw data from the TV

        if no timeout occurs but an empty response is received this is taken as
        an indication that the connection got terminated.

        :return: received data
        :rtype: str or None
        :raise: socket.timeout or socket.error
        """
        try:
            data = self._sock.recv(2048)
            if len(data) == 0:
                raise socket.timeout("Received 0 bytes -- disconnected?")

        except socket.timeout:
            _log(logging.DEBUG, "received nothing")
            raise
        except socket.error:
            raise
        else:
            _log(logging.DEBUG, "received %r  (timeout: %r)", data,
                 self._sock.gettimeout())
        return data

    def send(self, data):
        """
        send raw data to remote device

        if the connection to the remote device is not established,
        self.connect is called before sending th data.

        :param str data: binary data to send
        :return: bytes transmitted
        :rtype: int
        :raise: socket.timeout or socket.error
        """
        if self._sock is None:
            self.connect()
        try:
            _log(logging.DEBUG, "sending %r", data)
            return self._sock.send(data)
        except socket.timeout:
            _log(logging.warning, "Timeout when sending")
            raise
        except socket.error:
            _log(logging.warning, "Error in connection")
            raise
    
    def send_key(self, key):
        """
        send a key event to the device

        :param str key: key code to send. must start with "KEY_"
        :return: bytes transmitted via socket
        :rtype: int
        """
        msg = self._build_message("\x00", "\x00\x00\x00%s" % sstv_base64(key))
        return self.send(msg)

    def send_text(self, text):
        """
        send a text to the device

        texts can only be sent if specific fields are highlighted in the user 
        interface, eG password and user name fields, search fields, etc.

        :param str text: text to send
        :return: bytes transmitted via socket
        :rtype: int
        """
        msg = self._build_message("\x01", "\x01\x00%s" % sstv_base64(text))
        return self.send(msg)
    
    def _build_message(self, mode, payload):
        """
        internal helper - build message string

        :param str mode: message mode ('\x00' = keycode, '\x01' = text)
        :param str payload: message payload
        :return: encoded message
        """
        return "%s%s%s" % (mode, sstv_string(self.app_label + ".iapp.samsung"),
                           sstv_string(payload))

    def set_channel(self, channel, delay=None):
        """
        switch to a specific channel

        the given channel is padded to 4 digits and these are sent to the device
        as single key presses.

        :param int channel: channel to switch to (0 .. 9999)
        :param float delay: optional delay between key presses sent
        """
        map_ = dict((str(x), "KEY_%d" % x) for x in range(10))
        for digit in "%04d" % channel:
            self.send_key(map_[digit])
            if delay is not None:
                time.sleep(delay)
