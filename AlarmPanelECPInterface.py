#!/usr/bin/env python3

"""A class for interfacing with honeywell ECP BUS(keypad Bus)

   James Kozlowski
   https://github.com/jameskozlowski
   jameskozlowski.com

   TODO:
   Add support for other message types
"""

import serial
from enum import Enum

#bit backs to decode messages
BIT_MASK_BYTE1_BEEP         = 0x07
BIT_MASK_BYTE2_ARMED_STAY   = 0x80
BIT_MASK_BYTE2_LOW_BAT      = 0x40
BIT_MASK_BYTE2_READY        = 0x10
BIT_MASK_BYTE3_CHIME_MODE   = 0x20
BIT_MASK_BYTE3_BYPASS       = 0x10
BIT_MASK_BYTE3_AC_POWER     = 0x08
BIT_MASK_BYTE3_ARMED_AWAY   = 0x04


class AlarmMSGType(Enum):
    """ENUM for possible Alarm message types"""
    NONE = 0
    MESSAGE = 1
    STATUS = 2

class AlarmPanelECPInterface:
    """A class for interfacing with honeywell ECP BUS(keypad Bus)"""
    def __init__(self):
        """Setup the serial port with the correct settings"""
        self.serialPort = serial.Serial(
            port = '/dev/serial0',
            baudrate = 4800,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_TWO,
            bytesize = serial.EIGHTBITS)
    
    def __del__(self):
        """Close the serial port"""
        self.serialPort.close()

    def ReadPort(self, includeRawData = False):
        """Reads a byte from the serial port and check if it is a supported message type
           For now this class only support F7(display message) and F2(status change)
           return None if there is no msg or not a supported msg type
           if includeRawData is set to true raw data in included"""        
        buffer = ord(self.serialPort.read(1))

        if buffer == 0xF7:
            return self.ReadF7Msg(includeRawData)           
                
        elif buffer == 0xF2:
            return self.ReadF2Msg(includeRawData) 
                        
    def ReadF7Msg(self, includeRawData):
        """Parses a F7(display message) alarm message and returns a dic object
           if includeRawData is set to true raw data in included"""
        count = 1
        buffer = []
        buffer.append(0xF7)
        while count < 44:
                buffer.append(ord(self.serialPort.read(1)))
                count = count + 1
        msg = {}
        msg['type'] = AlarmMSGType.MESSAGE
        if includeRawData:
            msg['rawdata'] = buffer
        msg['address'] = buffer[3]
        msg['beep'] = ((buffer[6] & BIT_MASK_BYTE2_ARMED_STAY) > 0)
        msg['armedStay'] = ((buffer[7] & BIT_MASK_BYTE2_ARMED_STAY) > 0)
        msg['lowBat'] = ((buffer[7] & BIT_MASK_BYTE2_LOW_BAT) > 0)
        msg['ready'] = ((buffer[7] & BIT_MASK_BYTE2_READY) > 0)
        msg['chimeMode'] = ((buffer[8] & BIT_MASK_BYTE3_CHIME_MODE) > 0)
        msg['bypass'] = ((buffer[8] & BIT_MASK_BYTE3_BYPASS) > 0)
        msg['ACPower'] = ((buffer[8] & BIT_MASK_BYTE3_AC_POWER) > 0)
        msg['armedAway'] = ((buffer[8] & BIT_MASK_BYTE3_ARMED_AWAY) > 0)
        msg['msg'] = ''.join(chr(c) for c in buffer[12:44])
        return msg

    def ReadF2Msg(self, includeRawData):
        """Parses a F2(status change) alarm message and returns a dic object
        if includeRawData is set to true raw data in included"""
        count = 2
        buffer = []
        buffer.append(0xF2)
        buffer.append(ord(self.serialPort.read(1)))
        len = int(buffer[1]) + 2
        while count < len:
            buffer.append(ord(self.serialPort.read(1)))
            count = count + 1
        #messages with a len of less then 19 do not contain the data we need
        if buffer[1] < 19:
            return None
        msg = {}
        msg['type'] = AlarmMSGType.STATUS
        if includeRawData:
            msg['rawdata'] = buffer
        msg['armed'] = buffer[19] == 0x02
        msg['alarm'] = buffer[22] == 0x4
        return msg

if __name__ == "__main__":
    alarm = AlarmPanelECPInterface()
    while(1):
        msg = alarm.ReadPort()
        if msg and msg['type'] == AlarmMSGType.MESSAGE:
            print(msg['msg'])
        elif msg and msg['type'] == AlarmMSGType.STATUS:
            print(msg)
