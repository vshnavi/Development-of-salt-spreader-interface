# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#

from ICDLibrary import Message

from struct import unpack

import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename="Trial.log", level=logging.INFO)
__all__ = ["GetUnitStatusCmd", "GetUnitStatusRcv"]


class GetUnitStatusCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x12
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 0
        self._data = b''
        self.crc = 0


class GetUnitStatusRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.status = None
        self.error_bits = None

    def _format_data(self):
        return "Status info: 0x{0:08x},  Error bits: 0x{1:08x}\n".format(self.status, self.error_bits)

    def decode(self):
        Message.MessageFromDevice.decode(self)
        self.status = unpack("<I", self.data[0:4])[0]
        self.error_bits = unpack("<I", self.data[4:8])[0]
