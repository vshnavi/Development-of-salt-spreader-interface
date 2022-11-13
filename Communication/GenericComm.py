# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.

import threading
import logging
logger = logging.getLogger(__name__)


class GenericComm:

    buffer_size = 65536

    def __init__(self):
        self.stop_event = threading.Event()
        self.data_buffer = bytearray(GenericComm.buffer_size)
        self.byteHandler = None         # Only support one byteHandler at a time, this is enough for Zmodem purposes
        self._lock = threading.RLock()  # Re-entrant lock so that listener can also remove byteHandler
        self.listener_thread = None

    # These methods should be overridden in the derived classes to enable communication
    def open(self):
        """Open communication medium"""
        pass

    def close(self):
        """Open communication medium"""
        pass

    def send(self, data):
        """Send data"""
        return False

    def receive(self):
        """Receive data into buffer and return the number of bytes received"""
        return 0

    def start(self) -> object:
        if self.listener_thread and self.listener_thread.is_alive():
            return
        self.listener_thread = threading.Thread(target=self.listener)
        self.stop_event.clear()
        self.listener_thread.start()

    def stop(self):
        self.stop_event.set()
        # Thread cannot join itself. If listener calls stop from executing byteHandler,
        # simply set the event and the listener will stop before a new attempt to receive and handle data.
        if self.listener_thread and self.listener_thread != threading.current_thread():
            self.listener_thread.join()
        self.listener_thread = None

    def getBitsPerSecond(self):
        """Bit rate of the interface"""

        # Return a minimum number here, should be overridden when implmenting the interface
        return 9600

    def addByteHandler(self, handler):
        """Adds a consumer for received bytes"""
        with self._lock:
            self.byteHandler = handler

    def removeByteHandler(self):
        """Removes a consumer for received bytes"""
        with self._lock:
            self.byteHandler = None

    def is_stopped(self):
        return self.stop_event.is_set()

    def listener(self):
        while True:
            if self.is_stopped():
                break
            nbytes = self.receive()
            with self._lock:
                # Call byteHandler also when there is no data, as it may be interested in reception timeout
                if self.byteHandler:
                    self.byteHandler.receive(self.data_buffer, nbytes)
