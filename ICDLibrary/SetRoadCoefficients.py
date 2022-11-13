# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
from ICDLibrary import Message
from struct import unpack, pack

import logging
logger = logging.getLogger(__name__)

__all__ = ["SetRoadCoefficientsCmd", "SetRoadCoefficientsRcv"]

class SetRoadCoefficientsCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x31
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 12
        self._data = b'\x00\x00\x00'
        self.crc = 0
        
    def set_setRoadCoeffs(self, factor1, factor2, factor3):
        self._data = pack('<fff', factor1, factor2, factor3)
        self.length = len(self._data)


class SetRoadCoefficientsRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.success = None

    def _format_data(self):
        if self.success is not None:
            return "Success: {0:d}\n".format(self.success)
        else:
            return "Error writing data"

    def decode(self):
        Message.MessageFromDevice.decode(self)
        if self.error_code == 0:
            self.success = self.data[0]
            
