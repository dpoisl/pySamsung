"""listen to samsung device events"""
__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"

import threading
import socket
from . import errors 
from . import base


class Matcher(object):
    def __init__(self, type_=None, payload=None):
        self._type = type_
        self._payload = payload

    def match(self, message):
        if self._type is not None and message.type != self.type:
            return False
        if self._payload is not None and message.payload != self.payload:
            return False
        return Truea


class Receiver(base.Connection, threading.Thread):
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0, 
            recv_timeout=2.0, name=None):
        self._listeners = []
        self._stopping = False
        base.Connection.__init__(self, app_label, host, port, auth_timeout, 
                recv_timeout)
        threading.Thread.__init__(self, name=name)
        print "init done"

    def add_listener(self, listener, matcher=Matcher()):
        self._listeners.append((matcher, listener))

    def run(self):
        print 1
        self._stopping = False
        self.connect()
        while not self._stopping:
            print "."
            try:
                data = self.recv()
            except socket.timeout:
                d = None
            if d is None:
                continue
            else:
                msg = base.Message(d)
                for (matcher, listener) in self._listeners:
                    if matcher(msg):
                        listener(msg)
        self.disconnect()
        self._stopping = False

    def stop(self):
        self._stopping = True

    def join(self, timeout=None):
        self._stopping = True
        super(Receiver, self).join(timeout)
