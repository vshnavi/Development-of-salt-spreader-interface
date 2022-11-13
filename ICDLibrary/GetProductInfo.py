# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#

from ICDLibrary import Message
from struct import unpack
from collections import OrderedDict

import logging
logger = logging.getLogger(__name__)

__all__ = ["GetProductInfoCmd", "GetProductInfoRcv"]

class GetProductInfoCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x11
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 0
        self._data = b''
        self.crc = 0



class GetProductInfoRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.pairs = 0
        self.data_fields = OrderedDict()

    def _format_data(self):
        components = []
        for key in self.data_fields.keys():
            components.append('{0}: {1}'.format(key, self.data_fields[key]))
        return ',  '.join(components)


    def decode(self):
        Message.MessageFromDevice.decode(self)
        # In error cases there is no data
        if self.error_code == 0:
            self.pairs = unpack('B', self.data[0:1])[0]
            data_index = 1
            for k in range(self.pairs):
                keyLength = unpack('B', self.data[data_index:data_index+1])[0]
                data_index = data_index + 1
                key = self.data[data_index:data_index + keyLength].decode()
                data_index = data_index + keyLength

                valueLength = unpack('B', self.data[data_index:data_index+1])[0]
                data_index = data_index + 1
                value = self.data[data_index:data_index + valueLength].decode()
                data_index = data_index + valueLength

                self.data_fields[key] = value
