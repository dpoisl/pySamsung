__version__ = "0.1.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("Remote", "AuthenticationError", "ConnectionError", "TimeoutError")


from base64 import b64encode
import socket

KEYS = {# power
        "KEY_POWER": "", #tv: nothing
        "KEY_POWEROFF": "Turn device off",
        "KEY_POWERON": "", # tv: nothing
        # numpad
        "KEY_0": "Keypad 0",
        "KEY_1": "Keypad 1",
        "KEY_2": "Keypad 2",
        "KEY_3": "Keypad 3",
        "KEY_4": "Keypad 4",
        "KEY_5": "Keypad 5",
        "KEY_6": "Keypad 6",
        "KEY_7": "Keypad 7", 
        "KEY_8": "Keypad 8",
        "KEY_9": "Keypad 9",
        "KEY_11": "",
        "KEY_12": "", 
        # admin keys
        "KEY_3SPEED": "",
        "KEY_FACTORY": "", 
        # navigation
        "KEY_LEFT": "Left",
        "KEY_RIGHT": "Right",
        "KEY_UP": "Up",
        "KEY_DOWN": "Down",
        "KEY_ENTER": "Enter", 
        "KEY_RETURN": "Return / Back",
        "KEY_EXIT": "Exit", 
        "KEY_HELP": "Help",
        "KEY_HOME": "", 
        "KEY_GUIDE": "Program Guide",
        "KEY_MENU": "Menu",
        "KEY_TOOLS": "Tools", 
        "KEY_TOPMENU": "?? HELP ??", #TV: strange "home" menu?
        "KEY_INFO": "Info", 
        "KEY_CONTENTS": "Smart HUB / Contents",
        # volume, cannels
        "KEY_VOLDOWN": "Volume Up",
        "KEY_VOLUP": "Volume Down",
        "KEY_CHUP": "Channel Up",
        "KEY_CHDOWN": "Channel Down",
        "KEY_CH_LIST": "Channel List",
        "KEY_FAVCH": "Favourite Channels",
        "KEY_MUTE": "Mute", 
        "KEY_PRECH": "Previous Channel",
        # teletext
        "KEY_RED": "Red / A", #TV: ok
        "KEY_GREEN": "Green / B", #TV: ok
        "KEY_YELLOW": "Yellow / C", #TV: ok
        "KEY_CYAN": "Cyan / D", #TV: ok
        "KEY_TTX_MIX": "TTX Mode",
        "KEY_TTX_SUBFACE": "TTX Zoom",
        # play control
        "KEY_REWIND": "Rewind",
        "KEY_FF": "Fast Forward",
        "KEY_STOP": "Stop",
        "KEY_PLAY": "Play",
        "KEY_PAUSE": "Pause",
        "KEY_REC": "Record", 
        # DVD?
        "KEY_DISC_MENU": "",
        "KEY_DVR_MENU": "",
        "KEY_ANGLE": "", 
        # source selection
        "KEY_SOURCE": "Select Source", #TV: source menu
        "KEY_ANYNET": "",
        "KEY_HDMI": "HDMI",
        "KEY_HDMI1": "",
        "KEY_HDMI2": "",
        "KEY_HDMI3": "",
        "KEY_HDMI4": "", 
        "KEY_SVIDEO1": "",
        "KEY_SVIDEO2": "",
        "KEY_SVIDEO3": "",
        "KEY_ANTENA": "",
        "KEY_AV1": "",
        "KEY_AV2": "",
        "KEY_AV3": "",
        "KEY_COMPONENT1": "",
        "KEY_COMPONENT2": "", 
        # *?* ARC/ANYNET?
        "KEY_AUTO_ARC_ANYNET_MODE_OK": "",
        "KEY_AUTO_ARC_AUTOCOLOR_FAIL": "", 
        "KEY_AUTO_ARC_AUTOCOLOR_SUCCESS": "",
        "KEY_AUTO_ARC_CAPTION_ENG": "", 
        "KEY_AUTO_ARC_CAPTION_KOR": "",
        "KEY_AUTO_ARC_CAPTION_OFF": "", 
        "KEY_AUTO_ARC_CAPTION_ON": "",
        "KEY_AUTO_ARC_C_FORCE_AGING": "", 
        "KEY_AUTO_ARC_JACK_IDENT": "",
        "KEY_AUTO_ARC_USBJACK_INSPECT": "",
        "KEY_AUTO_ARC_LNA_ON": "",
        "KEY_AUTO_ARC_LNA_OFF": "", 
        "KEY_AUTO_ARC_RESET": "", 
        "KEY_AUTO_ARC_PIP_CH_CHANGE": "", 
        "KEY_AUTO_ARC_PIP_DOUBLE": "",
        "KEY_AUTO_ARC_PIP_LARGE": "", 
        "KEY_AUTO_ARC_PIP_LEFT_BOTTOM": "",
        "KEY_AUTO_ARC_PIP_LEFT_TOP": "", 
        "KEY_AUTO_ARC_PIP_RIGHT_BOTTOM": "",
        "KEY_AUTO_ARC_PIP_RIGHT_TOP": "", 
        "KEY_AUTO_ARC_PIP_SMALL": "",
        "KEY_AUTO_ARC_PIP_SOURCE_CHANGE": "", 
        "KEY_AUTO_ARC_PIP_WIDE": "",
        # aspect ratio switch?
        "KEY_ASPECT": "Aspect Ratio", #TV: aspect ratio
        "KEY_4_3": "", #TV: nothing
        "KEY_16_9": "", #TV: nothing
        # zoom control?
        "KEY_ZOOM1": "",
        "KEY_ZOOM2": "",
        "KEY_ZOOM_IN": "",
        "KEY_ZOOM_MOVE": "",
        "KEY_ZOOM_OUT": "", 
        # ?????
        "KEY_AD": "",
        "KEY_ADDDEL": "",
        "KEY_ALT_MHP": "",
        "KEY_ANYVIEW": "",
        "KEY_APP_LIST": "", 
        "KEY_AUTO_ARC_ANTENNA_AIR": "",
        "KEY_AUTO_ARC_ANTENNA_CABLE": "", 
        "KEY_AUTO_ARC_ANTENNA_SATELLITE": "",
        "KEY_AUTO_ARC_ANYNET_AUTO_START": "", 
        "KEY_AUTO_FORMAT": "",
        "KEY_AUTO_PROGRAM": "",
        "KEY_BACK_MHP": "",
        "KEY_BOOKMARK": "", 
        "KEY_CALLER_ID": "",
        "KEY_CAPTION": "",
        "KEY_CATV_MODE": "",
        "KEY_CLEAR": "", 
        "KEY_CLOCK_DISPLAY": "",
        "KEY_CONVERGENCE": "", 
        "KEY_CONVERT_AUDIO_MAINSUB": "",
        "KEY_CUSTOM": "", 
        "KEY_DEVICE_CONNECT": "",
        "KEY_DMA": "",
        "KEY_DNET": "", 
        "KEY_DNIe": "",
        "KEY_DNSe": "",
        "KEY_DOOR": "",
        "KEY_DSS_MODE": "",
        "KEY_DTV": "", 
        "KEY_DTV_LINK": "",
        "KEY_DTV_SIGNAL": "",
        "KEY_DVD_MODE": "",
        "KEY_DVI": "",
        "KEY_DVR": "", 
        "KEY_DYNAMIC": "",
        "KEY_ENTERTAINMENT": "",
        "KEY_ESAVING": "", 
        "KEY_FF_": "",
        "KEY_FM_RADIO": "",
        "KEY_GAME": "", #TV: message "not possible"
        "KEY_ID_INPUT": "",
        "KEY_ID_SETUP": "",
        "KEY_INSTANT_REPLAY": "", 
        "KEY_LINK": "",
        "KEY_LIVE": "", 
        "KEY_MAGIC_BRIGHT": "",
        "KEY_MAGIC_CHANNEL": "",
        "KEY_MDC": "",
        "KEY_MIC": "",
        "KEY_MORE": "",
        "KEY_MOVIE1": "",
        "KEY_MS": "",
        "KEY_MTS": "", 
        "KEY_NINE_SEPERATE": "",
        "KEY_OPEN": "",
        "KEY_PANORAMA": "",
        "KEY_PCMODE": "", 
        "KEY_PERPECT_FOCUS": "",
        "KEY_PICTURE_SIZE": "",
        "KEY_PLUS100": "",
        "KEY_PMODE": "",
        "KEY_PRINT": "",
        "KEY_PROGRAM": "",
        "KEY_QUICK_REPLAY": "",
        "KEY_REPEAT": "",
        "KEY_RESERVED1": "",
        "KEY_REWIND_": "",
        "KEY_RSS": "", 
        "KEY_RSURF": "",
        "KEY_SCALE": "",
        "KEY_SEFFECT": "",
        "KEY_SETUP_CLOCK_TIMER": "",
        "KEY_SLEEP": "",
        "KEY_SOUND_MODE": "",
        "KEY_SRS": "", 
        "KEY_STANDARD": "",
        "KEY_STB_MODE": "",
        "KEY_STILL_PICTURE": "",
        "KEY_SUB_TITLE": "", 
        "KEY_TURBO": "",
        "KEY_TV": "",
        "KEY_TV_MODE": "",
        "KEY_VCHIP": "", #HT: VCHIP
        "KEY_VCR_MODE": "", 
        "KEY_W_LINK": "", 
        "KEY_WHEEL_LEFT": "", #HT: volume wheel?
        "KEY_WHEEL_RIGHT": "", #HT: volume wheel?
        # PIP?
        "KEY_PIP_CHDOWN": "",
        "KEY_PIP_CHUP": "",
        "KEY_PIP_ONOFF": "",
        "KEY_PIP_SCAN": "",
        "KEY_PIP_SIZE": "", 
        "KEY_PIP_SWAP": "",
        # ?? extended keys? untested!
        "KEY_EXT1": "",
        "KEY_EXT2": "",
        "KEY_EXT3": "",
        "KEY_EXT4": "",
        "KEY_EXT5": "",
        "KEY_EXT6": "", 
        "KEY_EXT7": "",
        "KEY_EXT8": "",
        "KEY_EXT9": "",
        "KEY_EXT10": "",
        "KEY_EXT11": "", 
        "KEY_EXT12": "",
        "KEY_EXT13": "",
        "KEY_EXT14": "",
        "KEY_EXT15": "",
        "KEY_EXT16": "", 
        "KEY_EXT17": "",
        "KEY_EXT18": "",
        "KEY_EXT19": "",
        "KEY_EXT20": "",
        "KEY_EXT21": "", 
        "KEY_EXT22": "",
        "KEY_EXT23": "",
        "KEY_EXT24": "",
        "KEY_EXT25": "",
        "KEY_EXT26": "", 
        "KEY_EXT27": "",
        "KEY_EXT28": "",
        "KEY_EXT29": "",
        "KEY_EXT30": "",
        "KEY_EXT31": "", 
        "KEY_EXT32": "",
        "KEY_EXT33": "",
        "KEY_EXT34": "",
        "KEY_EXT35": "",
        "KEY_EXT36": "", 
        "KEY_EXT37": "",
        "KEY_EXT38": "",
        "KEY_EXT39": "",
        "KEY_EXT40": "",
        "KEY_EXT41": "", 
        # PANNEL?
        "KEY_PANNEL_CHDOWN": "",
        "KEY_PANNEL_CHUP": "",
        "KEY_PANNEL_ENTER": "", 
        "KEY_PANNEL_MENU": "",
        "KEY_PANNEL_POWER": "",
        "KEY_PANNEL_SOURCE": "", 
        "KEY_PANNEL_VOLDOW": "",
        "KEY_PANNEL_VOLUP": "", 
        }

LOCAL_MAC = "00:23:4d:b3:a2:cd" #TODO: get from interface?
TV_IP = "192.168.1.120"

class AuthenticationError(Exception):
    pass

class ConnectionError(Exception):
    pass

class TimeoutError(Exception):
    pass


def hexlen(string):
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
    return "%s%s" % (hexlen(string), string)


def lenstr64(string):
    """Shortcut: create lenstr of a base64 encoded string"""
    return lenstr(b64encode(string))


def parse_lenstr(src):
    length = ord(src[0]) + ord(src[1]) * 256
    return src[2:length+2]


class Remote(object):
    def __init__(self, app_label, ip, port=55000):
        self.ip = ip
        self.port = port
        self.app_label = app_label
        self._local_ip = None
        self._sock = None
        self._local_mac = None

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(5.0)
        try:
            self._sock.connect((self.ip, self.port))
        except socket.error:
            raise ConnectionError("Couldn't connect to %s:%d" % (self.ip, self.port))
        self._local_ip = self._sock.getsockname()[0]
        self._local_mac = LOCAL_MAC

        auth_content = "\x64\x00%s%s%s" % (lenstr64(self._local_ip),
                                           lenstr64(self._local_mac),
                                           lenstr64(self.app_label))
        auth = "\x00%s%s" % (lenstr(self.app_label + ".iapp.samsung"), 
                             lenstr(auth_content))
        try:
            self._sock.send(auth)
            auth_response = self._sock.recv(2048)
        except socket.timeout:
            raise TimeoutError("Timeout in authentication")
        
        sendapp = parse_lenstr(auth_response[1:])
        result = parse_lenstr(auth_response[1+2+len(sendapp):])
        
        if result == "\x64\x00\x01\x00":
            return True
        elif result == "\x64\x00\x00\x00":
            self._sock.close()
            raise AuthenticationError("access denied by remote device")
        elif result == "\x0a\x00\x02\x00\x00\x00":
            raise AuthenticationError("please allow this remote on your device")
        elif result == "\x64\x00":
            raise AuthenticationError("timeout")
        else:
            print("unknown result: %r" % result)
    
    def disconnect(self):
        self._sock.close()
        self._sock = None
    
    def send_key(self, key):
        return self._send(key)

    def send_text(self, text):
        return self._send(text, as_text=True)

    def _send(self, data, as_text=False):
        """send the given payload to the TV"""
        if self._sock is None:
            self.connect()

        if as_text:
            data_payload = "\x01\x00\x00%s" % lenstr64(data)
            mode = "\x01"
        else:
            data_payload = "\x00\x00\x00%s" % lenstr64(data)
            mode = "\x00"
        data = "%s%s%s" % (mode, lenstr(self.app_label + ".iapp.samsung"),
                             lenstr(data_payload))
        try:
            self._sock.send(data)
            d = self._sock.recv(2048)
        except socket.timeout:
            raise TimeoutError("failed to send data")
        except socket.error:
            raise ConnectionError("failed to send data")
        
        print("key/text result: %r" % d)
        return d


def list_keys(key=None):
    """get a list of possible keys with their description"""
    if key is None:
        return KEYS
    else:
        return dict((k, v) for (k, v) in key.items() if k.startswith(key))


class SamsungTV(object):
    """
    Remote control for a Samsung TV
    """
    def __init__(self, ip, port=55000, app_label="pyremote", model="UE40D5700"):
        """
        Arguments:
            ip          ip address of the TV
            port        remote control port (default 55000)
            app_label   name of the remote control app (used for authentication
                        on TV)
            model       TV model (optional, set this if you get problems)
        """
        self.app_label = app_label
        self.model = model
        self.ip = ip
        self.port = port
        self._local_ip = None
        self.local_mac = None
        self.get_local_mac()

    @property
    def long_app_string(self):
        return "%s.iapp.samsung" % self.app_label

    @property
    def tv_app_string(self):
        return "%s.%s.iapp.samsung" % (self.app_label, self.model)
    
    def get_local_mac(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        self.local_ip = sock.getsockname()[0]
        sock.close()
    
    def _gen_header(self):
        """generate message header"""
        inner_header = "d\x00%s%s%s" % (
                lenstr64(self.local_ip), 
                lenstr64(LOCAL_MAC),
                lenstr64(self.app_label))
        return "\x00%s%s\x00%s\x02\x00\xC8\x00" % (
                lenstr(self.long_app_string), 
                lenstr(inner_header), 
                lenstr(self.long_app_string))

    def _gen_request(self, text, key=True):
        """generate a request"""
        header = self._gen_header()
        if key:
            inner_payload = "\x00\x00\x00%s" % (lenstr64(text),)
        else:
            inner_payload = "\x01\x00%s" % (lenstr64(text),)
        if key:
            payload = "\x00%s%s" % (lenstr(self.tv_app_string),
                                    lenstr(inner_payload))
        else:
            payload = "\x01%s%s" % (lenstr(self.tv_app_string),
                                    lenstr(inner_payload))
        return "".join((header, payload))
        
    def send_key(self, key):
        """
        Send a single key to the TV

        This function sends a single keypress to the TV. Valid keys are
        defined in KEYS

        Arguments:
            key     key to send
        """
        if key not in KEYS:
            raise ValueError("invalid key: %r" % key)
        return self._send(self._gen_request(key))

    def send_text(self, text):
        """
        Send a text to the TV

        This function sends a given string to the TV (eG usable for text
        fields.

        Arguments:
            text    text to send
        """
        return self._send(self._gen_request(text, key=False))

    def set_channel(self, number):
        """
        Switch to a given channel

        This function takes a channel number and sends the corresponding
        keys to switch to the channel.

        Arguments:
            number: channel to switch to
        """
        map_ = {"0": "KEY_0",
               "1": "KEY_1",
               "2": "KEY_2",
               "3": "KEY_3",
               "4": "KEY_4",
               "5": "KEY_5",
               "6": "KEY_6",
               "7": "KEY_7",
               "8": "KEY_8",
               "9": "KEY_9"}
        for char in str(number):
            self.send_key(map_[char])
        self.send_key("KEY_ENTER")

    def _send(self, payload):
        """send the given payload to the TV"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.port))
        sock.send(payload)
        response = ""
        while(True):
            buffer_ = sock.recv(2048)
            if len(buffer_) < 2048:
                break
            response += buffer
        sock.close()
        return response
