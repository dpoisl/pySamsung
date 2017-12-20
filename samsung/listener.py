"""
listen to samsung device events

get notified when something happens on your TV
"""

from __future__ import unicode_literals

import threading
import socket
from samsung import base


__version__ = '0.3.0'
__author__ = 'David Poisl <david@poisl.at>'


class IterReceiver(base.SmartTV):
    """
    iterator-based receiver

    This can be used to listen for all events a Samsung Smart TV sends.
    It can be used as a generator which blocks while waiting for new messages
    received and yields them as processed samsung.Message instances.

    An optional filter function given to the constructor can be used to drop
    all messages that are not of interest. This function should be a callable
    taking a Message instance as its sole parameter and return True if the
    Message should be yielded, else False.
    """
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0,
                 recv_timeout=2.0, filter_=lambda x: True):
        """
        constructor

        :param str app_label: application label for authentication
        :param str host: host name or IP of the SmartTV
        :param int port: optional override for the remote port - default 55000
        :param float auth_timeout: timeout for authentication - default 20.0s
        :param float recv_timeout: timeout for message receiving - default 2.0s
        :param filter_: optional filter method for messages
        :return:
        """
        super(IterReceiver, self).__init__(app_label, host, port, auth_timeout,
                                           recv_timeout)
        self.filter = filter_
        self._connected = False

    def __iter__(self):
        """iter(self)"""
        return self

    def __next__(self):
        """next(self)"""
        if not self._connected:
            self.connect()
        while True:
            try:
                data = self.recv()
            except socket.timeout:
                continue
            except socket.error:
                raise

            msg = base.Message.parse(data)
            if self.filter(msg):
                return msg

    next = __next__  # python 2/3 compatibility


class ThreadReceiver(base.SmartTV, threading.Thread):
    """
    threaded receiver

    for the times where IterReceiver is not enough this can yield received
    Responses to multiple listeners in a threaded environment.

    use add_listener to add another receiver. The receiver should be a callable
    taking a Message instance as its only parameter. An optional second
    callable can be given as a filter for this listener.
    """
    def __init__(self, app_label, host, port=55000, auth_timeout=20.0,
                 recv_timeout=2.0, name=None):
        """
        constructor

        :param str app_label: application label for authentication
        :param str host: host name or IP of the SmartTV
        :param int port: optional override for the remote port - default 55000
        :param float auth_timeout: timeout for authentication - default 20.0s
        :param float recv_timeout: timeout for message receiving - default 2.0s
        :param str name: optional thread name
        :return:
        """
        self._listeners = []
        self._stopping = False
        base.SmartTV.__init__(self, app_label, host, port, auth_timeout,
                              recv_timeout)
        threading.Thread.__init__(self, name=name)

    def add_listener(self, listener, matcher=lambda x: True):
        """
        add another listener to the receiver

        the given listener will get notified for all Responses sent from the
        Smart TV. It should be a callable taking a Message instance as its
        only argument.
        An optional matcher function can be given which should be a callable
        taking a Message instance as its argument and return True for
        responses that should be sent to the listener.

        :param callable listener: callback for matching messages
        :param callable matcher: matcher for this listener.
        """
        self._listeners.append((matcher, listener))

    def run(self):
        """
        main loop for the listener thread
        """
        self._stopping = False
        self.connect()
        while not self._stopping:
            try:
                data = self.recv()
            except socket.timeout:
                continue

            try:
                msg = base.Message.parse(data)
            except ValueError:
                print('!!! could not parse %r' % data)
                continue
            for (matcher, listener) in self._listeners:
                if matcher(msg):
                    listener(msg)

        self.disconnect()
        self._stopping = False

    def stop(self):
        """
        stop thread gracefully

        :return:
        """
        self._stopping = True

    def join(self, timeout=None):
        """
        join thread gracefully

        :param float timeout: optional timeout for Thread.join()
        """
        self._stopping = True
        super(ThreadReceiver, self).join(timeout)
