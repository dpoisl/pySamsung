"""
Base functionality to communicate with Samsung Smart TVs.
"""

import base64
import enum
import socket
import logging
import uuid  # used for mac detection
import time

from typing import Optional, Tuple, Union


__version__ = '0.4.0'
__author__ = 'David Poisl <david@poisl.at>'

__all__ = ('sstv_string', 'sstv_base64', 'SmartTV', 'Message',
           'parse_sstv_string', 'AuthenticationError')


_logger: Optional[logging.Logger] = None
_mac = '%012x' % uuid.getnode()
LOCAL_MAC = ':'.join(_mac[i:i + 2] for i in range(0, 12, 2))


class AuthenticationError(Exception):
    """App is not authenticated."""
    pass


class ResponseType(enum.Enum):
    """
    Known response types.

    This information is extracted from tests with a Samsung UE40D5700 TV set
    and a HT-D5100 BluRay Home Theatre.

    KEY_CONFIRM key received while viewing TV
    STATE_CHANGE status update from SmartTV
    KEY_CONFIRM_MENU key received while in menu
    TIMESHIFT exact meaning unknown, somehow related to time-shift?
    """
    KEY_CONFIRM = 0x00
    KEY_CONFIRM_MENU = 0x01
    STATE_CHANGE = 0x02
    TIMESHIFT = 0x04


class ResponsePayload(enum.Enum):
    """
    container for known response payloads

    this information is extracted from tests with a Samsung UE40D5700 TV set
    and a HT-D5100 BluRay Home Theatre.

    AUTH_OK: authentication response: success
    AUTH_ACCESS_DENIED: authentication error: access denied
    AUTH_NEED_CONFIRMATION: authentication response: need
                            confirmation from user on TV?
    AUTH_TIMEOUT: authentication timeout
    KEY_OK: response payload for key events
    STATUS_SHOWING_MENU: seems to indicate that a menu is active
    STATUS_SHOWING_TV: seems to indicate that no menu is visible
    STATUS_SHOWING_TTX: seems to indicate that TTX is displayed
    STATUS_SHOWING_OVERLAY: sent for some overlays over TV
    """
    AUTH_OK = '\x64\x00\x01\x00'
    AUTH_ACCESS_DENIED = '\x64\x00\x00\x00'
    # TODO: on AUTH_NEED_CONFIRMATION: will OK/DENIED be sent later?

    AUTH_NEED_CONFIRMATION = '\x0a\x00\x02\x00\x00\x00'
    AUTH_TIMEOUT = '\x64\x00'
    KEY_OK = '\x00\x00\x00\x00'

    STATUS_SHOWING_MENU = '\x10\x00\x02\x00\x00\x00'
    STATUS_SHOWING_TV = '\x10\x00\x01\x00\x00\x00'
    STATUS_SHOWING_TTX = '\x10\x00\x0c\x00\x00\x00'
    STATUS_SHOWING_OVERLAY = '\x10\x00\x18\x00\x00\x00'


def set_logging(active: bool = True, logger_name: str = 'samsung.base'):
    """
    Activate debug messages.
    
    sets the global _logger either to None if active is false
    or to a logging.Logger instance with the given name. This
    enables or disables logging of debug messages.

    :param active: activate/deactivate logging (default: True)
    :param logger_name: name to use for the logger
    :return: the created logger
    """
    global _logger
    if active:
        logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(logger_name)
    else:
        _logger = None
    return _logger


def _log(level: int, message: str, *args, **kwargs) -> None:
    """
    Handles optional logging (only if set_logging was called with active=True).

    This internally calls logging.Logger.log() with all given arguments if
    a logger is initialized in the modules _logger variable.

    :param level: log level to use
    :param message: log message to send
    :param args: positional arguments for Logger.log call
    :param kwargs: keyword arguments for Logger.log call
    """
    if _logger is not None:
        return _logger.log(level, message, *args, **kwargs)


def sstv_string(string: Union[str, bytes]) -> bytes:
    """
    Convert a string to Samsungs string format.
    
    the samsung communication protocol encodes strings as 2 bytes containing
    the length, then a NULL byte and then the string itself.

    :param string: text to encode
    :return: the converted string
    """
    if isinstance(string, str):
        string = string.encode('ASCII')
    length = len(string)
    if length > 256 ** 2:
        raise ValueError('String too long')
    return bytes((length % 256, length // 256)) + string


def sstv_base64(string: str) -> bytes:
    """
    Shortcut: base64 encode a string and create a sstv_string of it.

    :param string: text to encode
    :return: the resulting sstv_string
    """
    return sstv_string(base64.b64encode(string.encode("ASCII")))


def parse_sstv_string(data: bytes) -> Tuple[str, bytes]:
    """
    Parse a string as returned by samsung devices.

    Samsung devices send strings with the length as the first two bytes 
    (little endian). This function can be used to get the content from
    these strings.

    :param data: source data
    :return: the parsed string and potentially remaining data
    """
    _log(logging.DEBUG, 'Parsing sstv_string %r', data)
    length = data[0] + data[1] * 256
    if len(data) < length + 2:
        raise ValueError('missing %d bytes in %r' % (length, data))
    _log(logging.DEBUG, 'Length %d, payload %r, remainder %r',
         length, data[2:length + 2], data[length + 2:])
    return data[2:length + 2].decode('ASCII'), data[length + 2:]


class Message:
    """
    A message sent by a samsung device.

    :ivar type: message type
    :ivar payload: message payload
    :ivar sender: name of the sending device
    """

    def __init__(self, type_: int, payload: str, sender: Optional[str] = None):
        """
        Constructor.

        :param int type_: message type
        :param str payload: message payload
        :param str sender: optional sender indicator
        """
        self.type = type_
        self.payload = payload
        self.sender = sender

    @classmethod
    def parse(cls, message: bytes) -> 'Message':
        """
        Parse a response as received on the network socket.

        :param message: payload received on socket
        :return: Message instance with parsed type, payload and sender
        """
        type_ = message[0]
        (sender, remaining) = parse_sstv_string(message[1:])
        (payload, remaining) = parse_sstv_string(remaining)
        if remaining:
            raise ValueError('Parser error: message %r, remaining data: %r' % (
                             message, remaining))
        return cls(type_, payload, sender)

    def __repr__(self) -> str:
        """textual representation"""
        return 'Message(sender=%s, type_=%x, payload=%r)' % (
            self.sender, self.type, self.payload)
    
    def __eq__(self, other: Union[str, 'Message']) -> bool:
        """
        Compare for equality.

        :param other: item to compare to
        :return: equality
        """
        if isinstance(other, bytes):
            return self.__eq__(Message.parse(other))
        elif isinstance(other, Message):
            return self.type == other.type and self.payload == other.payload
        else:
            return NotImplemented
    
    def __str__(self) -> str:
        """Get string representation."""
        return '%x:%r' % (self.type, self.payload)

    def __ne__(self, other: Union[str, 'Message']) -> bool:
        return not self.__eq__(other)


class SmartTV:
    """
    Connector for samsung SmartTV devices.

    Provides basic functionality like authentication, receiving and
    sending data. as well as higher level functionality like sending
    key codes or strings (eG for text input fields).

    :ivar app_label: application name (will be used in authentication)
    """
    def __init__(self, app_label: str, host: str, port: int = 55000,
                 auth_timeout: Union[int, float] = 20.0,
                 recv_timeout: Union[int, float] = 2.0):
        """
        Create a new connection.

        :param app_label: application label to use for authentication and
                          data transmission
        :param host: ip address or hostname of the device
        :param port: tcp port for remote control connection (default:
                     55000)
        :param auth_timeout: authentication timeout in seconds (
                             default: 20.0, None=wait forever)
        :param recv_timeout: timeout for message polling in seconds. (
                             default: 2.0, None = no timeout)
        """
        self._sockargs = (host, port)
        self.app_label = app_label
        self._sock = None
        self._auth_timeout = auth_timeout
        self._recv_timeout = recv_timeout
        self._auth_tries = 3

    def __repr__(self) -> str:
        return '%s(%r, %r, %r, %r, %r)' % (self.__class__.__name__,
                                           self.app_label, self._sockargs[0],
                                           self._sockargs[1],
                                           self._auth_timeout,
                                           self._recv_timeout)
    
    def connect(self) -> None:
        """Connect to device and authenticate."""
        self._connect()
        self._authenticate()
    
    def _connect(self) -> None:
        """
        Connect to the device socket.

        :raises: socket.error
        """
        _log(logging.DEBUG, 'Connecting to %s:%d', self._sockargs[0],
             self._sockargs[1])
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(self._auth_timeout)
        try:
            self._sock.connect(self._sockargs)
        except socket.error:
            raise

    def _authenticate(self) -> bool:
        """
        Authenticate with samsung device.

        Performs authentication with the samsung device and returns the
        authentication result. Raises AuthenticationError if the
        authentication failed.

        :return: True if authentication was successful
        :raises: AuthenticationError, socket.error
        """
        socket_name = self._sock.getsockname()[0]
        auth_content = b'\x64\x00' + sstv_base64(socket_name) + \
                       sstv_base64(LOCAL_MAC) + sstv_base64(self.app_label)
        auth = b'\x00' + sstv_string(self.app_label + '.iapp.samsung') + \
               sstv_string(auth_content)

        _log(logging.DEBUG, 'sending %r', auth)
        self._sock.send(auth)
        status = None

        for i in range(self._auth_tries):
            try:
                _log(logging.DEBUG, 'AUTH2 WAIT')
                response = self.recv()
                _log(logging.DEBUG, 'AUTH2 Response: %r' % response)
            except socket.timeout:
                _log(logging.DEBUG, 'AUTH2 timeout')
            else:
                status = self._parse_auth_response(response)
                _log(logging.DEBUG, '2nd AUTH RESPONSE: %r', status)
            if status:
                _log(logging.DEBUG, 'OK')
                self._sock.settimeout(self._recv_timeout)
                return True
        else:
            _log(logging.DEBUG, 'ERROR')
            raise AuthenticationError('access denied by remote device')

    def _parse_auth_response(self, response: bytes) -> Optional[bool]:
        """
        Parse authentication response.

        Parses the response to an authentication request and returns the
        success as boolean. If the device is still waiting for a
        confirmation from the user, None is returned instead.
    
        :param response: authentication response as string
        :return: None if no response received or we should wait, else
                 authentication result
        """
        if response is None:
            _log(logging.DEBUG, 'got no response')
            return None
        parsed = Message.parse(response)
        if parsed.payload == ResponsePayload.AUTH_OK:
            _log(logging.DEBUG, 'Authentication successful')
            return True
        elif parsed.payload == ResponsePayload.AUTH_ACCESS_DENIED:
            _log(logging.DEBUG, 'Authentication response: Access Denied')
            self._sock.close()
            return False
        elif parsed.payload == ResponsePayload.AUTH_NEED_CONFIRMATION:
            _log(logging.DEBUG, 'Authentication response: waiting for '
                 'confirmation on device')
            return None
        elif parsed.payload == ResponsePayload.AUTH_TIMEOUT:
            _log(logging.DEBUG, 'Authentication response: Timeout')
            raise AuthenticationError('timeout')
        else:
            _log(logging.DEBUG, 'Unknown authentication response')
            raise ValueError('unknown auth response: %r' % parsed)

    def disconnect(self) -> None:
        """Disconnect socket."""
        self._sock.close()
        self._sock = None
    
    def recv(self) -> bytes:
        """
        Receive raw data from the TV.

        If no timeout occurs but an empty response is received this is taken as
        an indication that the connection got terminated.

        :return: received data
        :rtype: str or None
        :raise: socket.timeout or socket.error
        """
        try:
            data = self._sock.recv(2048)
            if len(data) == 0:
                raise socket.timeout(1, 'Received 0 bytes -- disconnected?')

        except socket.timeout:
            _log(logging.DEBUG, 'received nothing')
            raise
        except socket.error:
            raise
        else:
            _log(logging.DEBUG, 'received %r  (timeout: %r)', data,
                 self._sock.gettimeout())
        return data

    def send(self, data: bytes) -> int:
        """
        Send raw data to remote device.

        If the connection to the remote device is not established,
        self.connect is called before sending th data.

        :param data: binary data to send
        :return: number of bytes transmitted
        :raise: socket.timeout or socket.error
        """
        if self._sock is None:
            self.connect()
        try:
            _log(logging.DEBUG, 'sending %r', data)
            return self._sock.send(data)
        except socket.timeout:
            _log(logging.WARNING, 'Timeout when sending')
            raise
        except socket.error:
            _log(logging.WARNING, 'Error in connection')
            raise
    
    def send_key(self, key: str) -> int:
        """
        Send a key event to the device.

        :param key: key code to send. must start with "KEY_"
        :return: number of bytes transmitted via socket
        """
        msg = self._build_message(0x00, b'\x00\x00\x00' + sstv_base64(key))
        return self.send(msg)

    def send_text(self, text: str) -> int:
        """
        Send a text to the device.

        Texts can only be sent if specific fields are highlighted in the user
        interface, eG password and user name fields, search fields, etc.

        :param text: text to send
        :return: number of bytes transmitted via socket
        """
        msg = self._build_message(0x01, b'\x01\x00' + sstv_base64(text))
        return self.send(msg)
    
    def _build_message(self, mode: int, payload: bytes) -> bytes:
        """
        Internal helper - build message string.

        :param mode: message mode (\x00 = keycode, \x01 = text)
        :param payload: message payload
        :return: encoded message
        """
        return bytes(mode) + sstv_string(self.app_label + '.iapp.samsung') \
            + sstv_string(payload)

    def set_channel(self, channel: str, delay: float = 0.1) -> None:
        """
        Switch to a specific channel by number.

        The given channel is padded to 4 digits and these are sent to the device
        as single key presses.

        :param int channel: channel to switch to (0 .. 9999)
        :param float delay: delay between key presses sent
        """
        map_ = {'0': 'KEY_0', '1': 'KEY_1', '2': 'KEY_2', '3': 'KEY_3',
                '4': 'KEY_4', '5': 'KEY_5', '6': 'KEY_6', '7': 'KEY_7',
                '8': 'KEY_8', '9': 'KEY_9'}
        for digit in '%04d' % channel:
            self.send_key(map_[digit])
            if delay:
                time.sleep(delay)
