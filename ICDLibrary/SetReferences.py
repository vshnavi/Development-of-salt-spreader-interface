# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
from ICDLibrary import Message
from struct import unpack, pack

import logging
logger = logging.getLogger(__name__)

__all__ = ["SetReferencesCmd", "SetReferencesRcv","StopReferenceSettingCmd","StopReferenceSettingRcv"]


class SetReferencesCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x30
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 1
        self._data = b'\x00'
        self.crc = 0
        
    def set_setRefType(self, refType):
        if refType >= 0:
            self._data = pack('<B', refType)


class SetReferencesRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.success = None
        self.status = None
        self.error_bits = None

    def _format_data(self):
        if self.success is not None:
            return "Success: {0:d}, Status info: 0x{1:08x},  Error bits: 0x{2:08x}\n".format(self.success, self.status, self.error_bits)
        else:
            return "Could not start reference setting \n"

    def decode(self):
        Message.MessageFromDevice.decode(self)
        if self.error_code == 0:
            self.success = self.data[0]
            self.status = unpack("<I", self.data[1:5])[0]
            self.error_bits = unpack("<I", self.data[5:9])[0]


class StopReferenceSettingCmd(Message.MessageToDevice):

    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x32
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 0
        self._data = b''
        self.crc = 0


class StopReferenceSettingRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)

    def _format_data(self):
        return "Stop reference setting ack"

    def decode(self):
        Message.MessageFromDevice.decode(self)
        logger.debug("Stop Reference Setting Ack Received")
