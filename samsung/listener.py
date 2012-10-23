"""listen to samsung device events"""
__version__ = "1.0.0"
__author__ = "David Poisl <david@poisl.at>"

import threading
import socket
import time
from . import errors 
from . import base


class Matcher(object):
    def __init__(self, type_=None, payload=None):
        self._type = type_
        self._payload = payload

    def __call__(self, message):
        if self._type is not None and message.type != self._type:
            return False
        if self._payload is not None and message.payload != self.payload:
            return False
        return True


class IterReceiver(base.Connection):
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0,
            recv_timeout=2.0, filter_=lambda x: True):
        super(IterReceiver, self).__init__(app_label, host, port, auth_timeout, 
                                           recv_timeout)
        self.filter = filter_
        self._connected = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self._connected:
            self.connect()
        while True:
            try:
                data = self.recv()
            except socket.timeout:
                continue
            msg = base.Response(data)
            if self.filter(msg):
                return msg

    next = __next__


class ThreadReceiver(base.Connection, threading.Thread):
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0, 
            recv_timeout=2.0, name=None):
        self._listeners = []
        self._stopping = False
        base.Connection.__init__(self, app_label, host, port, auth_timeout, 
                recv_timeout)
        threading.Thread.__init__(self, name=name)

    def add_listener(self, listener, matcher=Matcher()):
        self._listeners.append((matcher, listener))

    def run(self):
        self._stopping = False
        self.connect()
        while not self._stopping:
            try:
                data = self.recv()
            except socket.timeout:
                continue
            if data is None:
                continue

            try:
                msg = base.Response(data)
            except:
                print("!!! could not parse %r" % data)
                continue
            for (matcher, listener) in self._listeners:
                if matcher(msg):
                    listener(msg)
        
        self.disconnect()
        self._stopping = False

    def stop(self):
        print "stopping"
        self._stopping = True

    def join(self, timeout=None):
        print "joining"
        self._stopping = True
        super(ThreadReceiver, self).join(timeout)
