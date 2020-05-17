"""CLI entry points for samsung remote."""

__author__ = 'David Poisl <david@poisl.at>'
__version__ = '1.0.0'


from argparse import ArgumentParser
import datetime
import os
import time

from samsung import listener, base

base.set_logging(True)


def debug_print(message):
    """
    print messages from the server

    :param base.Message message: received message to print
    """
    print('--- %s ---\n%r\n' % (str(datetime.datetime.now()), message))


def listen():
    """Basic listener."""
    base.set_logging(True)
    l = listener.ThreadReceiver('pyremote', '192.168.1.120')
    l.add_listener(debug_print)
    l.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        l.stop()



def parse_remote_options():
    """
    Parse command line arguments and options.

    :return: options and arguments
    """
    description = '''Send commands to Samsung D-Series (and up) devices.
Commands can either start with 'KEY_' and be a valid key code or any
text (eG usable for password fields, etc.).'''
    p = ArgumentParser(description=description)
    p.add_argument('-i', '--ip', dest='ip',
                   help='Device IP (mandatory if you don\'t set '
                        'SAMSUNG_DEVICE in your environment)')
    p.add_argument('-p', '--port', dest='port', action='store', type=int,
                   default='55000', help='Device Port (default %(default)s')
    p.add_argument('-d', '--delay', dest='delay', action='store', type=float,
                   default='0.5', help='Delay between commands in seconds ('
                                       'default: %(default)s')
    p.add_argument('keys', nargs='+')
    args = p.parse_args()
    if args.ip is None:
        try:
            args.ip = os.environ['SAMSUNG_DEVICE']
        except KeyError:
            p.error('Either set SAMSUNG_DEVICE in the environment or specify '
                    'the device IP\n')
    if len(args.keys) == 0:
        p.error('Please specify one or more commands to send\n')
    return args


def remote():
    """Entry point to remote control a TV"""
    (options, args) = parse_remote_options()
    device = base.SmartTV('pyremote', host=options.ip, port=options.port)
    for arg in args:
        if arg.startswith('KEY_'):
            print('%r' % device.send_key(arg))
        elif arg.startswith('CH'):
            for digit in '%04d' % int(arg[2:]):
                device.send_key('KEY_' + digit)
        else:
            print('%r' % device.send_text(arg))
        time.sleep(options.delay)
        print('%r' % base.Message.parse(device.recv()))
        print('%r' % base.Message.parse(device.recv()))
        print('%r' % base.Message.parse(device.recv()))
    device.disconnect()
