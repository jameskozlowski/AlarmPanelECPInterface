# AlarmPanelECPInterface
A python interface for connecting to a honeywell ECP BUS(keypad Bus)
I built this library to allow me to connect a R PI Zero W to my alarm panel so I could send an email to myself when the alarm goes off

I plan to add more features such as:
- emulate a keypad so I can arm and unarm remotely

# Functions
### ReadPort(includeRawData = False)
Reads a byte from the serial port and check if it is a supported message type
For now, this class only support F7(display message) and F2(status change)

parameter|Disc.
---------|----
includeRawData|if set to true the raw binary data is included in the return object default: False
**RETURNS**|None if there was not message to return

# Return Objects

check the msg['type'] before reading values

**AlarmMSGType.MESSAGE**
Key|Disc.
---------|----
type|The Type of message returned
rawdata|The binary raw data if requests
address|The address of the keypad the msg was meant for
beep|True if the keypad should beep
armedStay|True if the alarm is armed in 'stay' mode
lowBat|True if the battery is low (or not installed)
ready|True if the alarm is ready to arm
chimeMode|True if the door chime is enabled
bypass|True if a zone is bypassed
ACPower|True if the alarm has AC power
armedAway|True if the alarm is armed in 'away' mode
msg|The string message the keypad should display

<BR>

**AlarmMSGType.STATUS**
Key|Disc.
---------|----
type|The Type of message returned
armed|True if the alarm is armed
alarm|True if the alarm is tripped

There is other date encoded in this MSG but I did not bother to decode it

# Example

```
import AlarmPanelECPInterface

alarm = AlarmPanelECPInterface()

while(1):
    #check for a new message
    msg = alarm.ReadPort()

    #check for a message type
    if msg and msg['type'] == AlarmMSGType.MESSAGE:
        print(msg['msg'])
    elif msg and msg['type'] == AlarmMSGType.STATUS:        
        if msg['alarm']:
            print("ALARM!!")
            #send email
```

# Hardware Setup
This python library was meant to run on a Raspberry Pi Zero W, but should work on other Raspberrys or even other device running python with a serial connection to the alarm panel.

This library is for one way communication  only from the panel. the panel ECP BUS is a from of RS-232 with the signals inverted.

**CONNECT AT YOUR OWN RISK**
I made my connections using  a opto-coupler, this simple method allows you to invert the signal, provide some isolation and bring the voltage level down

![RS-232 Connection](img/sch.png?raw=true "Title")
![R PI Zero W Connection](img/rpi.png?raw=true "Title")


# More Information
 Miguel Sanchez's article in Circuit Cellar. "Reverse-Engineered ECP Bus, article 2007 year from the Circuit Cellar magazine."

 https://github.com/TANC-security/keypad-firmware