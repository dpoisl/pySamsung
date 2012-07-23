"""
Samsung remote control library
"""


__version__ = "0.1.0"
__author__ = "David Poisl <david@poisl.at>"

__all__ = ("Remote",)


from . import base

class Remote(base.Connection):
    def send_key(self, key):
        """
        send a key event to the device

        arguments:
        key -- key code to send, must start with "KEY_"
        """
        msg = self._build_message(mode="\x00", 
                                 payload="\x00\x00\x00%s" % base.lenstr64(key))
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
                                  payload="\x01\x00%s" % base.lenstr64(text))
        return self.send(msg)
    
    def _build_message(self, mode, payload):
        """internal helper - build a message"""
        return "%s%s%s" % (mode, base.lenstr(self.app_label + ".iapp.samsung"),
                           base.lenstr(payload))

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
       


#class SamsungTV(object):
#    """DEPRECATED Remote control for a Samsung TV"""
#    def __init__(self, host, port=55000, app_label="pyremote", model=""):
#        """
#        Arguments:
#            host        ip address of the TV
#            port        remote control port (default 55000)
#            app_label   name of the remote control app (used for authentication
#                        on TV)
#            model       TV model (optional, set this if you get problems)
#        """
#        self.app_label = app_label
#        self.model = model
#        self.host = host 
#        self.port = port
#        self._local_host = None
#        self.local_mac = None
#        self.get_local_mac()
#
#    @property
#    def long_app_string(self):
#        return "%s.iapp.samsung" % self.app_label
#
#    @property
#    def tv_app_string(self):
#        #return "%s.%s.iapp.samsung" % (self.app_label, self.model)
#        return "%s.iapp.samsung" % self.app_label
#    
#    def get_local_mac(self):
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        sock.connect((self.host, self.port))
#        self.local_host = sock.getsockname()[0]
#        sock.close()
#    
#    def _gen_header(self):
#        """generate message header"""
#        inner_header = "d\x00%s%s%s" % (
#                base.lenstr64(self.local_host), 
#                base.lenstr64(self._local_mac),
#                base.lenstr64(self.app_label))
#        return "\x00%s%s\x00%s\x02\x00\xC8\x00" % (
#                base.lenstr(self.long_app_string), 
#                base.lenstr(inner_header), 
#                base.lenstr(self.long_app_string))
#
#    def _gen_request(self, text, key=True):
#        """generate a request"""
#        header = self._gen_header()
#        if key:
#            inner_payload = "\x00\x00\x00%s" % (base.lenstr64(text),)
#        else:
#            inner_payload = "\x01\x00%s" % (base.lenstr64(text),)
#        if key:
#            payload = "\x00%s%s" % (base.lenstr(self.tv_app_string),
#                                    base.lenstr(inner_payload))
#        else:
#            payload = "\x01%s%s" % (base.lenstr(self.tv_app_string),
#                                    base.lenstr(inner_payload))
#        return "".join((header, payload))
#        
#    def send_key(self, key):
#        """
#        Send a single key to the TV
#
#        This function sends a single keypress to the TV. Valid keys are
#        defined in KEYS
#
#        Arguments:
#            key     key to send
#        """
#        if key not in KEYS:
#            raise ValueError("invalid key: %r" % key)
#        return self.send(self._gen_request(key))
#
#    def send_text(self, text):
#        """
#        Send a text to the TV
#
#        This function sends a given string to the TV (eG usable for text
#        fields.
#
#        Arguments:
#            text    text to send
#        """
#        return self.send(self._gen_request(text, key=False))
#
#    def set_channel(self, number):
#        """
#        Switch to a given channel
#
#        This function takes a channel number and sends the corresponding
#        keys to switch to the channel.
#
#        Arguments:
#            number: channel to switch to
#        """
#        map_ = {"0": "KEY_0",
#               "1": "KEY_1",
#               "2": "KEY_2",
#               "3": "KEY_3",
#               "4": "KEY_4",
#               "5": "KEY_5",
#               "6": "KEY_6",
#               "7": "KEY_7",
#               "8": "KEY_8",
#               "9": "KEY_9"}
#        for char in str(number):
#            self.send_key(map_[char])
#        self.send_key("KEY_ENTER")
#
#    def send(self, payload):
#        """send the given payload to the TV"""
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        sock.connect((self.host, self.port))
#        sock.send(payload)
#        print "-> %r" % payload
#        response = ""
#        while True:
#            buffer_ = sock.recv(2048)
#            response += buffer_
#            print "<- %r" % buffer_
#            if len(buffer_) == 0:
#                break
#        sock.close()
#        return response
