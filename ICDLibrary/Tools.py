# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
__all__ = ["hexify"]

def hexify(data):
    # Helper method for converting bytes object into hex string.
    # This is required in Python 2, where bytearray does not print nicely by itself and bytes is actually a string.
    bdata = bytearray(data)
    return ' '.join('0x{:02x}'.format(x) for x in bdata)
