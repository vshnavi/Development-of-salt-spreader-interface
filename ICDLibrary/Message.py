# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#


from binascii import crc_hqx
from struct import pack, unpack
import pandas as pd
from matplotlib import pyplot as plt

import logging
logger = logging.getLogger(__name__)


class MessageToDevice(object):
    """Base class for messages sent to MD30 device.

    Individual message types can be derived from this to add content specific helper methods.
    """

    def __init__(self):
        logger.debug("Initialing {0}".format(type(self).__name__))

        # Structured data
        print('messge file se kya aya')
        plt.rcParams["figure.figsize"] = [7.00, 3.50]
        plt.rcParams["figure.autolayout"] = True
        columns = ["AirT", "Time"]
        df = pd.read_csv("csvfile.csv", usecols=columns)
        x = df.AirT
        y = df.Time
        plt.plot(x, y)
        plt.show()
        print("Contents in csv file:\n", df)
        self.startMarker = None
        self.senderId = None
        self.receiverId = None
        self.id = None
        self.number = None
        self.length = None
        # data is defined as a protected member, and should not usually be directly accessed.
        # Child classes (commands) that contain data should define data members (with or without accessors)
        # that are updated by user, and override encode() to first update _data from those, then call
        # MessageToDevice.encode() that converts _data and the common fields into bytes.
        self._data = None
        self.crc = None

    def set_checksum(self):
        """Compute the checksum corresponding to current values of data fields and set it in message."""
        byte_data = self.encode()
        self.crc = crc_hqx(byte_data[1:-2], 0xffff)
        print('messge file se kya aya2222')

    def encode(self):
        """Return a bytes object matching the current data in the message.

        Length of the return value corresponds to length of 'data' member, not necessarily 'length' field if they are
        in conflict. Note that also the checksum is taken from the message, not computed here. Use set_checksum() first
        to set the correct checksum."""

        data_length = len(self._data)

        byte_data = bytearray(7 + data_length + 2)
        byte_data[0] = 0xAB
        byte_data[1] = self.senderId
        byte_data[2] = self.receiverId
        byte_data[3] = self.id
        byte_data[4] = self.number
        byte_data[5] = self.length & 0xFF;
        byte_data[6] = (self.length >> 8) & 0xFF;
        if data_length > 0:
            byte_data[7: 7 + data_length] = self._data
        byte_data[-2:] = pack('<H', self.crc)

        return byte_data


class MessageFromDevice(object):
    """Base class for messages received from  MD30 device.

    Individual message types can be derived from this to add content specific helper methods.
    """

    def __init__(self, byte_data):
        logger.debug("Initialing {0}".format(type(self).__name__))

        self.startMarker = None
        self.id = None
        self.senderId = None
        self.receiverId = None
        self.number = None
        self.length = None
        self.if_version = None
        self.error_code = None
        self.data = None
        self.crc = None

        # Initial bytes data
        if len(byte_data) < 11:
            raise ValueError("Message data too short")
        self._byte_data = byte_data

    def __str__(self):
        ret_string = "Unit ID: {0}, Client ID: {1}, ID: 0x{2:x},  Nb: {3},  Len: {4}, ".format(self.senderId, self.receiverId, self.id, self.number, self.length)
        if_version_string = "icd_version: " + chr(self.if_version) + ", Err: " + format(self.error_code) + "\n"
        ret_string = ret_string + if_version_string + self._format_data()
        return ret_string

    def _format_data(self):
        """Formats the variable data part into a string, must be overridden in each message class."""
        return ""

    def check_checksum(self):
        """Check whether the message checksum corresponds to data.

        This only operates on the bytes data given in the constructor. It can then be called before attempting to
        parse the message data."""

        crc_in_data = unpack('<H', self._byte_data[-2:])[0]
        crc_of_data = crc_hqx(self._byte_data[1:-2], 0xffff)
        return crc_in_data == crc_of_data

    def decode(self):
        """Update structured data to match byte data."""

        self.startMarker = self._byte_data[0]
        self.senderId = self._byte_data[1]
        self.receiverId = self._byte_data[2]
        self.id = self._byte_data[3]
        self.number = self._byte_data[4]
        self.length = unpack('<H', self._byte_data[5:7])[0]
        self.if_version = self._byte_data[7]
        self.error_code = self._byte_data[8]

        # Variable data content must be handled in message specific classes.
        self.data = self._byte_data[9:-2]

        # This method should be extended in child classes to handle also the variable data. It is probably best there
        # to parse only self.data member, which has been set based on internal _byte_data above.
        self.crc = unpack('<H', self._byte_data[-2:])[0]
