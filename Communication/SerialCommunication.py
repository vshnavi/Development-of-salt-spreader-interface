# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.

import serial

from Communication.GenericComm import GenericComm


class SerialCommunication(GenericComm):
    def __init__(self):
        GenericComm.__init__(self)
        # Long write timeout, but do not block indefinitely
        self._serial = serial.Serial(write_timeout=2.0)
        self._serial.timeout = 0.5

    def set_port(self, port):
        self._serial.port = port

    def set_baudrate(self, rate):
        self._serial.baudrate = rate

    def open(self):
        self._serial.open()

    def close(self):
        if not self.is_stopped():
            self.stop()
        self._serial.close()

    def settimeout(self, timeout):
        self._serial.timeout = timeout

    def send(self, data):
        try:
            nbytes = self._serial.write(data)
        except serial.SerialTimeoutException:
            nbytes = 0
        return nbytes == len(data)

    def receive(self):
        nbytes = self._serial.readinto(self.data_buffer)
        return nbytes

    def getBitsPerSecond(self):
        return self._serial.baudrate
