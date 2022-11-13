# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#

from ICDLibrary import Message

import logging
logger = logging.getLogger(__name__)

__all__ = ["RestartUnitCmd", "RestartUnitRcv"]


class RestartUnitCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x50
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 0
        self._data = b''
        self.crc = 0


class RestartUnitRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)

    def _format_data(self):
        return "RESET ACK"

    def decode(self):
        Message.MessageFromDevice.decode(self)
        logger.debug("Reset Ack Received")
