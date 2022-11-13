# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#

from ICDLibrary import Message
from struct import pack, unpack
from datetime import datetime
import pytz
import xlsxwriter
import logging
import time

# current_date_and_time = datetime.now()
# current_time = current_date_and_time.strftime("%d.%m.%Y %H:%M:%S,%f")
# current_time = datetime.now(pytz.timezone('US/Eastern')).strftime("%d.%m.%Y %H:%M:%S")

# current_time = time.ctime()
# print(current_time)
# print(current_date_and_time)
import matplotlib.pyplot as plt

import matplotlib.animation as animation




workbook = xlsxwriter.Workbook('Example2.xlsx')
worksheet = workbook.add_worksheet()

logger = logging.getLogger(__name__)

__all__ = ["SendDataCmd", "SendDataRcv"]
print('check 1')


class SendDataCmd(Message.MessageToDevice):
    def __init__(self):
        Message.MessageToDevice.__init__(self)
        self.id = 0x20
        self.senderId = 0
        self.receiverId = 1
        self.number = 0
        self.length = 2
        self._data = b'\x00\x00'
        self.crc = 0

    print(Message.MessageToDevice)

    def set_interval(self, interval):
        print('iinterval\n\n', interval)
        self._data = pack('<H', interval)


class SendDataRcv(Message.MessageFromDevice):

    def __init__(self, byte_data):
        Message.MessageFromDevice.__init__(self, byte_data)
        # Instead of separate date members use a dictionary for easier access
        self.data_fields = {}

    print('SendDataRCV')

    def _format_data(self):
        if self.error_code == 0:
            format_string = "W: {Water:6.2f}, I: {Ice:6.2f}, S: {Snow:6.2f}, G: {Grip:6.2f}, St: {State:d}, EN: {EN15518State:d}"
            format_string += ", TA: {AirT:6.2f}, RH: {RH:6.2f}, DP: {DewPoint:6.2f}, FP: {FrostPoint:6.2f}, TS {SurfaceT:6.2f}"
            format_string += ", C: {AnalyzeCount:5d}, DW: 0x{DataWarning:04x}, DE: 0x{DataError:04x}, USt: 0x{UnitStatus:08x}, UE: 0x{ErrorBits:08x}"
        else:
            format_string = ""
        return format_string.format(**self.data_fields)

    def decode(self):
        row = 0
        col = 0
        Message.MessageFromDevice.decode(self)
        print('yay')
        # In error cases there is no data although the message ID matches.
        if self.error_code == 0:
            bytes_format = '<3H5f2B4f2I'
            data = unpack(bytes_format, self.data[0:52])
            # Same names as in test library
            names = ["AnalyzeCount",
                     "DataWarning",
                     "DataError",
                     "AirT",
                     "RH",
                     "DewPoint",
                     "FrostPoint",
                     "SurfaceT",
                     "State",
                     "EN15518State",
                     "Grip",
                     "Water",
                     "Ice",
                     "Snow",
                     "UnitStatus",
                     "ErrorBits"]
            self.data_fields.update(zip(names, data))
            # print(names)
            # print(data)
        print('SendDataRCV.decode')
        current_time = datetime.now(pytz.timezone('US/Eastern')).strftime("%d.%m.%Y %H:%M:%S")
        print(current_time)

        # No extra formatting for debug, simply output the dictionary.
        logging.basicConfig(filename="Try.log", encoding='utf-8', level=logging.DEBUG)
        print("Decoded message: {0}".format(str(self.data_fields)))
        # logging.debug("Decoded message: {0}".format(str(self.data_fields)))
        logging.debug("Test")


        with open('csvfile.csv', 'a') as f:
            datas = []
            for names, data in zip(names, data):
                datas.append(data)
                # worksheet.write(row, col, names)
                # worksheet.write(row, col + 1, data)
                # row += 1
            f.write(
                '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(datas[0], datas[1], datas[2], datas[3],
                                                                              datas[4], datas[5], datas[6], datas[7],
                                                                              datas[8], datas[9], datas[10], datas[11],
                                                                              datas[12], datas[13], datas[14],
                                                                              datas[15], current_time))


            # # Set up plot to call animate() function periodically
            # ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
            # plt.show()




    # def animate(i, xs, ys, self=None):
    #     Message.MessageFromDevice.decode(self)
    #     print('yay1')
    #     # In error cases there is no data although the message ID matches.
    #     if self.error_code == 0:
    #         bytes_format = '<3H5f2B4f2I'
    #         data = unpack(bytes_format, self.data[0:52])
    #         # Same names as in test library
    #         names = ["AnalyzeCount",
    #                  "DataWarning",
    #                  "DataError",
    #                  "AirT",
    #                  "RH",
    #                  "DewPoint",
    #                  "FrostPoint",
    #                  "SurfaceT",
    #                  "State",
    #                  "EN15518State",
    #                  "Grip",
    #                  "Water",
    #                  "Ice",
    #                  "Snow",
    #                  "UnitStatus",
    #                  "ErrorBits"]
    #         self.data_fields.update(zip(names, data))
    #         print(names)
    #         print(data)
    #         print('in animate mode')
    #
    #         ys.append(current_time)
    #         xs.append(datas[4])
    #         ax.clear()
    #         ax.plot(xs, ys)
    #
    #         # Format plot
    #         plt.xticks(rotation=45, ha='right')
    #         plt.subplots_adjust(bottom=0.30)
    #         plt.title('Temperature over Time')
    #         plt.ylabel('Temperature (deg C)')
        # No extra formatting for debug, simply output the dictionary.
        # logging.basicConfig(filename="Try.log", encoding='utf-8', level=logging.DEBUG)
        # print("Decoded message: {0}".format(str(self.data_fields)))
        # logging.debug("Decoded message: {0}".format(str(self.data_fields)))
        # logging.debug("Test")
# v=SendDataCmd.set_interval(100)
# #v.decode(1000)
