"""
Samsung remote control library
"""


__version__ = "0.1.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("Remote",)


from . import errors
from . import base

KEYS = (# power
        "KEY_POWER", "KEY_POWEROFF", "KEY_POWERON",
        # numpad
        "KEY_0", "KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_5", "KEY_6", "KEY_7", 
        "KEY_8", "KEY_9", "KEY_11", "KEY_12", 
        # admin keys
        "KEY_3SPEED", "KEY_FACTORY", 
        # navigation
        "KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN", "KEY_ENTER", 
        "KEY_RETURN", "KEY_EXIT", "KEY_HELP", "KEY_HOME",  "KEY_GUIDE", 
        "KEY_MENU", "KEY_TOOLS", "KEY_TOPMENU", "KEY_INFO", "KEY_CONTENTS", 
        # volume, cannels
        "KEY_VOLDOWN", "KEY_VOLUP", "KEY_CHUP", "KEY_CHDOWN", "KEY_CH_LIST",
        "KEY_FAVCH", "KEY_MUTE", "KEY_PRECH",
        # teletext
        "KEY_RED", "KEY_GREEN", "KEY_YELLOW", "KEY_CYAN", "KEY_TTX_MIX", 
        "KEY_TTX_SUBFACE",
        # play control
        "KEY_REWIND", "KEY_FF", "KEY_STOP", "KEY_PLAY", "KEY_PAUSE", "KEY_REC",
        # DVD?
        "KEY_DISC_MENU", "KEY_DVR_MENU", "KEY_ANGLE", 
        # source selection
        "KEY_SOURCE", "KEY_ANYNET", "KEY_HDMI", "KEY_HDMI1", "KEY_HDMI2", 
        "KEY_HDMI3", "KEY_HDMI4", "KEY_SVIDEO1", "KEY_SVIDEO2", "KEY_SVIDEO3", 
        "KEY_ANTENA", "KEY_AV1", "KEY_AV2", "KEY_AV3", "KEY_COMPONENT1", 
        "KEY_COMPONENT2",  
        # *?* ARC/ANYNET?
        "KEY_AUTO_ARC_ANYNET_MODE_OK", "KEY_AUTO_ARC_AUTOCOLOR_FAIL", 
        "KEY_AUTO_ARC_AUTOCOLOR_SUCCESS", "KEY_AUTO_ARC_CAPTION_ENG", 
        "KEY_AUTO_ARC_CAPTION_KOR", "KEY_AUTO_ARC_CAPTION_OFF", 
        "KEY_AUTO_ARC_CAPTION_ON", "KEY_AUTO_ARC_C_FORCE_AGING", 
        "KEY_AUTO_ARC_JACK_IDENT", "KEY_AUTO_ARC_USBJACK_INSPECT",
        "KEY_AUTO_ARC_LNA_ON", "KEY_AUTO_ARC_LNA_OFF", 
        "KEY_AUTO_ARC_RESET", "KEY_AUTO_ARC_PIP_CH_CHANGE", 
        "KEY_AUTO_ARC_PIP_DOUBLE", "KEY_AUTO_ARC_PIP_LARGE", 
        "KEY_AUTO_ARC_PIP_LEFT_BOTTOM", "KEY_AUTO_ARC_PIP_LEFT_TOP", 
        "KEY_AUTO_ARC_PIP_RIGHT_BOTTOM", "KEY_AUTO_ARC_PIP_RIGHT_TOP", 
        "KEY_AUTO_ARC_PIP_SMALL", "KEY_AUTO_ARC_PIP_SOURCE_CHANGE", 
        "KEY_AUTO_ARC_PIP_WIDE",
        # aspect ratio switch?
        "KEY_ASPECT", "KEY_4_3", "KEY_16_9", 
        # zoom control?
        "KEY_ZOOM1", "KEY_ZOOM2", "KEY_ZOOM_IN", "KEY_ZOOM_MOVE", 
        "KEY_ZOOM_OUT", 
        # ?????
        "KEY_AD", "KEY_ADDDEL", "KEY_ALT_MHP", "KEY_ANYVIEW", "KEY_APP_LIST", 
        "KEY_AUTO_ARC_ANTENNA_AIR", "KEY_AUTO_ARC_ANTENNA_CABLE", 
        "KEY_AUTO_ARC_ANTENNA_SATELLITE", "KEY_AUTO_ARC_ANYNET_AUTO_START", 
        "KEY_AUTO_FORMAT", "KEY_AUTO_PROGRAM", "KEY_BACK_MHP", "KEY_BOOKMARK", 
        "KEY_CALLER_ID", "KEY_CAPTION", "KEY_CATV_MODE", "KEY_CLEAR", 
        "KEY_CLOCK_DISPLAY", "KEY_CONVERGENCE", "KEY_CONVERT_AUDIO_MAINSUB",
        "KEY_CUSTOM", "KEY_DEVICE_CONNECT", "KEY_DMA", "KEY_DNET", "KEY_DNIe",
        "KEY_DNSe", "KEY_DOOR", "KEY_DSS_MODE", "KEY_DTV", "KEY_DTV_LINK",
        "KEY_DTV_SIGNAL", "KEY_DVD_MODE", "KEY_DVI", "KEY_DVR", "KEY_DYNAMIC",
        "KEY_ENTERTAINMENT", "KEY_ESAVING", "KEY_FF_", "KEY_FM_RADIO",
        "KEY_GAME", "KEY_ID_INPUT", "KEY_ID_SETUP", "KEY_INSTANT_REPLAY", 
        "KEY_LINK", "KEY_LIVE", "KEY_MAGIC_BRIGHT", "KEY_MAGIC_CHANNEL", 
        "KEY_MDC", "KEY_MIC", "KEY_MORE", "KEY_MOVIE1", "KEY_MS", "KEY_MTS", 
        "KEY_NINE_SEPERATE", "KEY_OPEN", "KEY_PANORAMA", "KEY_PCMODE", 
        "KEY_PERPECT_FOCUS", "KEY_PICTURE_SIZE", "KEY_PLUS100", "KEY_PMODE",
        "KEY_PRINT", "KEY_PROGRAM", "KEY_QUICK_REPLAY", "KEY_REPEAT", 
        "KEY_RESERVED1", "KEY_REWIND_", "KEY_RSS",  "KEY_RSURF", "KEY_SCALE",
        "KEY_SEFFECT", "KEY_SETUP_CLOCK_TIMER", "KEY_SLEEP", "KEY_SOUND_MODE",
        "KEY_SRS", "KEY_STANDARD", "KEY_STB_MODE", "KEY_STILL_PICTURE",
        "KEY_SUB_TITLE", "KEY_TURBO", "KEY_TV", "KEY_TV_MODE", 
        "KEY_VCHIP", "KEY_VCR_MODE", "KEY_W_LINK", "KEY_WHEEL_LEFT", 
        "KEY_WHEEL_RIGHT", 
        # PIP?
        "KEY_PIP_CHDOWN", "KEY_PIP_CHUP", "KEY_PIP_ONOFF", "KEY_PIP_SCAN",
        "KEY_PIP_SIZE", "KEY_PIP_SWAP",
        # ?? extended keys? untested!
        "KEY_EXT1", "KEY_EXT2", "KEY_EXT3", "KEY_EXT4", "KEY_EXT5",
        "KEY_EXT6", "KEY_EXT7", "KEY_EXT8", "KEY_EXT9", "KEY_EXT10",
        "KEY_EXT11", "KEY_EXT12", "KEY_EXT13", "KEY_EXT14", "KEY_EXT15",
        "KEY_EXT16", "KEY_EXT17", "KEY_EXT18", "KEY_EXT19", "KEY_EXT20",
        "KEY_EXT21", "KEY_EXT22", "KEY_EXT23", "KEY_EXT24", "KEY_EXT25",
        "KEY_EXT26", "KEY_EXT27", "KEY_EXT28", "KEY_EXT29", "KEY_EXT30",
        "KEY_EXT31", "KEY_EXT32", "KEY_EXT33", "KEY_EXT34", "KEY_EXT35",
        "KEY_EXT36", "KEY_EXT37", "KEY_EXT38", "KEY_EXT39", "KEY_EXT40",
        "KEY_EXT41", 
        # PANNEL?
        "KEY_PANNEL_CHDOWN", "KEY_PANNEL_CHUP", "KEY_PANNEL_ENTER", 
        "KEY_PANNEL_MENU", "KEY_PANNEL_POWER", "KEY_PANNEL_SOURCE", 
        "KEY_PANNEL_VOLDOW", "KEY_PANNEL_VOLUP", 
        )


class Remote(base.Connection):
    def send_key(self, key):
        mode = "\x00"
        payload = "\x00\x00\x00%s" % base.lenstr64(data)
        return self._send(self._build_message(mode, payload))

    def send_text(self, text):
        mode = "\x01"
        payload = "\x01\x00%s" % base.lenstr64(text)
        return self._send(self._build_message(mode, payload))
    
    def _build_message(self, mode, payload):
        data = "%s%s%s" % (mode, base.lenstr(self.app_label + ".iapp.samsung"),
                           base.lenstr(payload))



class SamsungTV(object):
    """DEPRECATED Remote control for a Samsung TV"""
    def __init__(self, host, port=55000, app_label="pyremote", model=""):
        """
        Arguments:
            host        ip address of the TV
            port        remote control port (default 55000)
            app_label   name of the remote control app (used for authentication
                        on TV)
            model       TV model (optional, set this if you get problems)
        """
        self.app_label = app_label
        self.model = model
        self.host = host 
        self.port = port
        self._local_host = None
        self.local_mac = None
        self.get_local_mac()

    @property
    def long_app_string(self):
        return "%s.iapp.samsung" % self.app_label

    @property
    def tv_app_string(self):
        #return "%s.%s.iapp.samsung" % (self.app_label, self.model)
        return "%s.iapp.samsung" % self.app_label
    
    def get_local_mac(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.local_host = sock.getsockname()[0]
        sock.close()
    
    def _gen_header(self):
        """generate message header"""
        inner_header = "d\x00%s%s%s" % (
                base.lenstr64(self.local_host), 
                base.lenstr64(self._local_mac),
                base.lenstr64(self.app_label))
        return "\x00%s%s\x00%s\x02\x00\xC8\x00" % (
                base.lenstr(self.long_app_string), 
                base.lenstr(inner_header), 
                base.lenstr(self.long_app_string))

    def _gen_request(self, text, key=True):
        """generate a request"""
        header = self._gen_header()
        if key:
            inner_payload = "\x00\x00\x00%s" % (base.lenstr64(text),)
        else:
            inner_payload = "\x01\x00%s" % (base.lenstr64(text),)
        if key:
            payload = "\x00%s%s" % (base.lenstr(self.tv_app_string),
                                    base.lenstr(inner_payload))
        else:
            payload = "\x01%s%s" % (base.lenstr(self.tv_app_string),
                                    base.lenstr(inner_payload))
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
        sock.connect((self.host, self.port))
        sock.send(payload)
        print "-> %r" % payload
        response = ""
        while True:
            buffer_ = sock.recv(2048)
            response += buffer_
            print "<- %r" % buffer_
            if len(buffer_) == 0:
                break
        sock.close()
        return response
