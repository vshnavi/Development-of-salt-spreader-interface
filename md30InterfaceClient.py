# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
# md30 interface client demonstrates the features of the MD30 serial interface.
#
# Requirements:
# - Python 3.7.x
# - PySerial
from xlsxwriter import workbook

import ICDLibrary
from Communication import SerialCommunication
import Interpreter
from ICDLibrary import GetUnitId, SendData
from MessageReceiver import MessageReceiver

import logging
import argparse
import time

# Import extra plugins if they are available
try:
    import Extras.Setup as Extras
except ImportError:
    Extras = None
    pass

def setup_logger():
    # Setup logger to print everything to log and only info+higher to the console
    global logger
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)

    # Select here the details wanted for logging output:
    # use this line to get time and logging level along with the message
    # formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Use this for simplistic output
    formatter = logging.Formatter('%(message)s')

    stream_handler = logging.StreamHandler()

    # Select lowest logging level to be shown on the console
    stream_handler.setLevel(logging.INFO)
    # stream_handler.setLevel(logging.DEBUG)

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    print("logger")

class MessageHandler:
    """Trivial message handler. Simply parses and logs the message."""

    def __init__(self):
        pass

    def receive_message(self, databuffer, datalen):
        # Must have header + CRC
        if datalen < 11 or len(databuffer) < datalen:
            logger.debug("Message with invalid length in Handler")
            return

        response = ICDLibrary.MessageFactory.create_received_message(databuffer[0:datalen])
        if response:
            response.decode()
            for line in str(response).split("\n"):
                logger.info(line)
            if not response.check_checksum():
                logger.warning("Warning: invalid checksum!")
        else:
            logger.warning("Unidentified message: {0}".format(ICDLibrary.hexify(databuffer[0:datalen])))

    print("MessageReceiver")

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", help="execute commands from file")

    serial_group = parser.add_argument_group("Serial Client related options")
    serial_group.add_argument("--port-name", "-P", default="COM3")
    serial_group.add_argument("--baud-rate", "-B", type=int, default=115200)

    if Extras:
        Extras.add_extra_arguments(parser)

    opts = parser.parse_args()
    return opts
    print("Argumentparser")

if __name__ == "__main__":
    setup_logger()

    options = parse_args()

    if Extras:
        comm = Extras.create_comm(options)
    else:
        # Setup basic serial communications
        comm = SerialCommunication.SerialCommunication()
        comm.set_port(options.port_name)
        comm.set_baudrate(options.baud_rate)

    comm.settimeout(0.05)
    comm.open()

    message_handler = MessageHandler()
    receiver = MessageReceiver(message_handler)
    comm.addByteHandler(receiver)
    comm.start()
    print("Main")
    cmd = Interpreter.MD30SerialCmd(comm)

    if options.file:
        # This inserts commands from the file into the command queue. They are interpreted once cmdloop() is started.
        cmd.onecmd("source {}".format(options.file))
        # Exit after the file has been executed
        cmd.cmdqueue.append("bye")



    # Interpret commands
    version = 2.0
    interface_version = "C"
    version_string = "MD30 interface client version {0}\nInterface version {1}\nCopyright (c) Vaisala Oyj. All rights reserved.".format(version, interface_version)
    cmd.intro = "Welcome to MD30 interface client. MD30 interface client demonstrates the features of the MD30 serial interface.\n\n" + version_string
    cmd.doc_leader = "\n" + version_string + "\n"
    #cmd.onecmd(GetUnitId)
    cmd.cmdloop()

    # Small wait to get any remaining messages before hanging out
    time.sleep(0.3)

    comm.stop()
    comm.close()


