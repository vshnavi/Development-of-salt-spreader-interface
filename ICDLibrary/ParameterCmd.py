# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#

from ICDLibrary import Message
from struct import pack, unpack
from collections import namedtuple
import struct
from enum import Enum

import logging
logger = logging.getLogger(__name__)

__all__ = ["GetParameterCmd", "GetParameterRcv", "SetParameterCmd", "SetParameterCmdError", "SetParameterRcv"]

Parameter = namedtuple('Parameter', ['id', 'format', 'description'])
parameter_definitions = [
    Parameter(0x10, '<B', 'Baud rate'),
    Parameter(0x11, '<B', 'Send CRC ack'),
    Parameter(0x12, '<B', 'Latest error code'),
    Parameter(0x13, '<B', 'Sensor ID'),
    Parameter(0x14, '<B', 'Autosend target ID'),
    Parameter(0x20, '<H', 'Autosend data interval'),
    Parameter(0x21, '<B', 'Autosend enabled'),
    Parameter(0x30, '<B', 'Temperature unit'),
    Parameter(0x31, '<B', 'Thickness unit'),
    Parameter(0x40, '<f', 'Road T offset'),
    Parameter(0x41, '<f', 'Air T offset'),
    Parameter(0x50, '<f', 'Reference value of laser 1'),
    Parameter(0x51, '<f', 'Reference value of laser 2'),
    Parameter(0x52, '<f', 'Reference value of laser 3'),
    Parameter(0x53, '<f', 'Reference setting value of laser 1'),
    Parameter(0x54, '<f', 'Reference setting value of laser 2'),
    Parameter(0x55, '<f', 'Reference setting value of laser 3'),
    Parameter(0x56, '<I', 'Reference setting error code'),
    Parameter(0x60, '<H', 'Extended data interval'),
    Parameter(0x61, '<B', 'Extended data autosend enabled')
]


class GetParameterCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x40
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 2
        self._data = b'\x00\x00'
        self.crc = 0

    def set_parameter(self, paramId):
        self._data = pack('<H', paramId)


class GetParameterRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        self.paramId = None
        self.value = None
        self.description = None

    def _format_data(self):
        if self.value is not None:
            if type(self.value) == float:
                return "ID: 0x{0:02X}  Value: {1:.5f}  ({2})\n".format(self.paramId, self.value, self.description)
            else:
                return "ID: 0x{0:02X}  Value: {1}  ({2})\n".format(self.paramId, self.value, self.description)
        else:
            return "Error reading data"

    def decode(self):
        Message.MessageFromDevice.decode(self)
        if self.error_code == 0:
            self.paramId = unpack('<H', self.data[0:2])[0]
            for p in parameter_definitions:
                if p.id == self.paramId:
                    try:
                        self.value = unpack(p.format, self.data[2:])[0]
                    except struct.error:
                        if p.id == 0x56:
                            # MD30 version 1.0.0 uses byte
                            self.value = unpack('<B', self.data[2:])[0]
                    self.description = p.description
                    break
            logger.debug("Decoded message: 0x{0:04X}: {1}".format(self.paramId, self.value))


class SetParameterCmdError(Enum):
    noError = 0
    invalidParameterId = 1
    invalidValueFormat = 2


class SetParameterCmd(Message.MessageToDevice):

    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x41
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 2
        self._data = b'\x00\x00'
        self.crc = 0
        self.errorCode = SetParameterCmdError.noError

    def set_parameter(self, paramId, value):
        data_format = None
        self.errorCode = SetParameterCmdError.noError
        for p in parameter_definitions:
            if p.id == paramId:
                data_format = p.format
                break
        if not data_format:
            """ Build the message even if the id was not found. Let the MD30
                check the id. MD30 will respond with error code 4 if it does
                not recognize the id.
            """
            self.errorCode = SetParameterCmdError.invalidParameterId
            data_format = '<B'
        if data_format:
            data_format = '<H' + data_format[1]
            try:
                self._data = pack(data_format, paramId, value)
                self.length = len(self._data)
            except struct.error:
                if self.errorCode is SetParameterCmdError.noError:
                    self.errorCode = SetParameterCmdError.invalidValueFormat


class SetParameterRcv(Message.MessageFromDevice):
    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
