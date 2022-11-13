# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.

from struct import unpack
from ICDLibrary import Tools

import logging
logger = logging.getLogger()
#logging.setLevel()  __name__

class ReceiverState:
    WAIT_START_MARKER = 0
    WAIT_SENDERID = 1
    WAIT_RECEIVERID = 2
    WAIT_ID = 3
    WAIT_NUMBER = 4
    WAIT_DATALEN = 5
    # interface version and error code treated as part of data
    WAIT_DATA = 6
    WAIT_CRC = 7


class MessageReceiver:
    # Binary data buffer size. Enough for all relevant (and currently specified messages).
    DATA_LEN = 1024
    START_MARKER = 0xAB

    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.data = bytearray(self.DATA_LEN)
        # These are reset below, but "declare" them in init already
        self.state = ReceiverState.WAIT_START_MARKER
        self.dataLen = 0
        self.msgDataLen = 0
        self.lowByte = False
        self.logger = None
        self.reset()

    def set_echo(self, enable, stream=None):
        if enable and self.logger is None:
            # Pass also raw serial output echo via logger in case in needs redirection to file or GUI window.
            rawlogger = logging.getLogger(__name__ + ".raw")
            rawlogger.setLevel(level=logging.INFO)
            rawlogger.propagate = False
            formatter = logging.Formatter('%(message)s')
            handler = logging.StreamHandler(stream)
            handler.terminator = ''
            handler.setFormatter(formatter)
            rawlogger.addHandler(handler)
            self.logger = rawlogger
        if not enable and self.logger is not None:
            self.logger = None

    def next_byte(self, b):
        if self.state == ReceiverState.WAIT_START_MARKER and b != MessageReceiver.START_MARKER:
            if self.logger:
                self.logger.info("0x"+format(b, '02x'))
            return False

        # Always add received bytes to the data buffer, unless we were waiting for start marker and did not get it.
        if self.dataLen < self.DATA_LEN:
            self.data[self.dataLen] = b
            self.dataLen = self.dataLen + 1
        else:
            self.reset()

        if self.state == ReceiverState.WAIT_START_MARKER and b == MessageReceiver.START_MARKER:
            self.state = ReceiverState.WAIT_SENDERID
        elif self.state == ReceiverState.WAIT_SENDERID:
            self.state = ReceiverState.WAIT_RECEIVERID
        elif self.state == ReceiverState.WAIT_RECEIVERID:
            self.state = ReceiverState.WAIT_ID
        elif self.state == ReceiverState.WAIT_ID:
            self.state = ReceiverState.WAIT_NUMBER
        elif self.state == ReceiverState.WAIT_NUMBER:
            self.state = ReceiverState.WAIT_DATALEN
        elif self.state == ReceiverState.WAIT_DATALEN:
            if self.lowByte:
                self.msgDataLen = unpack('<H', self.data[5:7])[0]
                self.state = ReceiverState.WAIT_DATA
                self.lowByte = False
            else:
                self.lowByte = True
        elif self.state == ReceiverState.WAIT_DATA:
            # Equality should be enough, but add greater than condition
            # to avoid getting stuck if something goes wrong
            # At this point total message data length is 7 larger than the data part of the message.
            if self.dataLen >= self.msgDataLen + 7:
                self.state = ReceiverState.WAIT_CRC
        elif self.state == ReceiverState.WAIT_CRC:
            if self.lowByte:
                # Message is complete
                self.lowByte = False
                return True
            else:
                self.lowByte = True
        else:
            logger.debug("Invalid Receiver state")
            self.reset()

        return False

    def reset(self, print_data=True):
        if print_data:
            self.print_received_data()
        self.state = ReceiverState.WAIT_START_MARKER
        self.dataLen = 0
        self.msgDataLen = 0
        self.lowByte = False

    def receive(self, databuffer, nbytes):
        """Handle bytes received from interface, while waiting command response"""

        if nbytes == 0:
            # Reception timed out
            self.reset(self.dataLen != 0)
        for i in range(0, nbytes):
            if self.next_byte(databuffer[i]):
                self.print_received_data()
                self.message_handler.receive_message(self.data, self.dataLen)
                self.reset(False)

    def print_received_data(self):
        if self.logger:
            self.logger.info(Tools.hexify(self.data[0:self.dataLen]))
            self.logger.info('\n')