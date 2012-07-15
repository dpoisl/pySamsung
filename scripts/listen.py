#!/usr/bin/python

from samsung import listener
import datetime
from time import sleep


def debug_print(message):
    """debug print a message"""
    print "--- %s ---\n%r\n    (%r)" % (str(datetime.datetime.now()), message, 
            message._raw_data)


if __name__ == "__main__":
    l = listener.ThreadReceiver("pysamsung", "192.168.1.120")
    l.add_listener(debug_print)
    l.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        l.stop()

