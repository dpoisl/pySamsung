#!/usr/bin/python

from samsung import listener

def debug_print(message):
    print message
    print "    (%r)" % message._raw_data

l = listener.Receiver("pysamsung", "192.168.1.120")
l.add_listener(debug_print)
l.start()
