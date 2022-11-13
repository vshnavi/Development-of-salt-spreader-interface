# Vaisala software source code file
#
# Copyright (c) Vaisala Oyj. All rights reserved.
#
from ICDLibrary import GetUnitId, GetProductInfo, GetUnitStatus, SendData, ParameterCmd, RestartUnit, SetReferences, SetRoadCoefficients

import logging
logger = logging.getLogger(__name__)


class MessageFactory:

    MessageDict = {
        0x10: GetUnitId.GetUnitIdRcv,
        0x11: GetProductInfo.GetProductInfoRcv,
        0x12: GetUnitStatus.GetUnitStatusRcv,
        0x20: SendData.SendDataRcv,
        0x30: SetReferences.SetReferencesRcv,
        0x31: SetRoadCoefficients.SetRoadCoefficientsRcv,
        0x32: SetReferences.StopReferenceSettingRcv,
        0x40: ParameterCmd.GetParameterRcv,
        0x41: ParameterCmd.SetParameterRcv,
        0x50: RestartUnit.RestartUnitRcv
    }

    @staticmethod
    def create_received_message(data):
        if len(data) < 4:
            raise ValueError("Insufficient data in MessageFactory")
        message_id = data[3]

        if message_id in MessageFactory.MessageDict:
            return MessageFactory.MessageDict[message_id](data)
        else:
            return None

    @staticmethod
    def register_response_message(id, message):
        """Add message to a list of known messages"""
        MessageFactory.MessageDict[id] = message
