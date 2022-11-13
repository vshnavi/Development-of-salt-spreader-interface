# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
import serial

from ICDLibrary import Message

import logging
logger = logging.getLogger(__name__)

__all__ = ["GetUnitIdCmd", "GetUnitIdRcv"]

class GetUnitIdCmd(Message.MessageToDevice):
    def __init__(self) -> object:
        Message.MessageToDevice.__init__(self)
        self.id = 0x10
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 0
        self._data = b''
        self.crc = 0


class GetUnitIdRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.serial = None

    def _format_data(self):
        return "Serial number: {0}\n".format(self.serial)

    def decode(self):
        Message.MessageFromDevice.decode(self)
        self.serial = self.data.decode()
        print('Hell0')
        logger.debug("Decoded message: {0}".format(self.serial))



