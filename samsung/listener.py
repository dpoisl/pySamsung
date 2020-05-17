"""
Listen to samsung device events.

Get notified when something happens on your TV.
"""

import socket
import threading
from typing import Callable, Union, Optional

from samsung import base


__version__ = '0.4.0'
__author__ = 'David Poisl <david@poisl.at>'


class IterReceiver(base.SmartTV):
    """
    Iterator-based receiver.

    This can be used to listen for all events a Samsung Smart TV sends.
    It can be used as a generator which blocks while waiting for new messages
    received and yields them as processed samsung.Message instances.

    An optional filter function given to the constructor can be used to drop
    all messages that are not of interest. This function should be a callable
    taking a Message instance as its sole parameter and return True if the
    Message should be yielded, else False.
    """
    def __init__(self, app_label: str, host: str, port: int = 55000,
                 auth_timeout: Union[float, int] = 20.0,
                 recv_timeout: Union[float, int] = 2.0,
                 filter_: Callable = lambda x: True):
        """
        Constructor.

        :param app_label: application label for authentication
        :param host: host name or IP of the SmartTV
        :param port: optional override for the remote port - default 55000
        :param auth_timeout: timeout for authentication - default 20.0s
        :param recv_timeout: timeout for message receiving - default 2.0s
        :param filter_: optional filter method for messages
        """
        super().__init__(app_label, host, port, auth_timeout, recv_timeout)
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


class ThreadReceiver(base.SmartTV, threading.Thread):
    """
    Threaded receiver.

    For the times where IterReceiver is not enough this can yield received
    Responses to multiple listeners in a threaded environment.

    Use add_listener to add another receiver. The receiver should be a callable
    taking a Message instance as its only parameter. An optional second
    callable can be given as a filter for this listener.
    """

    def __init__(self, app_label: str, host: str, port: int = 55000,
                 auth_timeout: Union[float, int] = 20.0,
                 recv_timeout: Union[float, int] = 2.0,
                 name: Optional[str] = None):
        """
        constructor

        :param app_label: application label for authentication
        :param host: host name or IP of the SmartTV
        :param port: optional override for the remote port - default 55000
        :param auth_timeout: timeout for authentication - default 20.0s
        :param recv_timeout: timeout for message receiving - default 2.0s
        :param name: optional thread name
        """
        self._listeners = []
        self._stopping = False
        base.SmartTV.__init__(self, app_label, host, port, auth_timeout,
                              recv_timeout)
        threading.Thread.__init__(self, name=name)

    def add_listener(self, listener: Callable,
                     matcher: Callable = lambda x: True) -> None:
        """
        Add another listener to the receiver.

        the given listener will get notified for all Responses sent from the
        Smart TV. It should be a callable taking a Message instance as its
        only argument.
        An optional matcher function can be given which should be a callable
        taking a Message instance as its argument and return True for
        responses that should be sent to the listener.

        :param listener: callback for matching messages
        :param matcher: matcher for this listener.
        """
        self._listeners.append((matcher, listener))

    def run(self) -> None:
        """Main loop for the listener thread."""
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

    def stop(self) -> None:
        """Stop thread gracefully."""
        self._stopping = True

    def join(self, timeout: Optional[float] = None) -> None:
        """
        Join thread gracefully.

        :param timeout: optional timeout for Thread.join()
        """
        self._stopping = True
        super(ThreadReceiver, self).join(timeout)
