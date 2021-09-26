#
# USB serial communication for the Raspberry Pi Pico (RD2040) using the second RD2040
# thread/processor (written by Dorian Wiskow - Janaury 2021) 
#
from sys import stdin, exit
from _thread import start_new_thread
from utime import sleep
# 
# global variables to share between both threads/processors
#
bufferSize = 1024                 # size of circular buffer to allocate
buffer = [' '] * bufferSize       # circuolar incomming USB serial data buffer (pre fill)
bufferEcho = True                 # USB serial port echo incooming characters (True/False) 
bufferNextIn, bufferNextOut = 0,0 # pointers to next in/out character in circualr buffer

###############################################################################
# for MCP41xxx
address = 0x11
value_i = 0
Rab = 10000  # 10k ohm
###############################################################################
# SPI Settings

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(17, machine.Pin.OUT)
cs.value(1)
# Initialize SPI
spi = machine.SPI(0,
                  baudrate=1000000,
                  polarity=1,
                  phase=1,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))

###############################################################################


# Functions

def digitalPotWrite(value):
    
    global address
    
    cmd = bytearray()
    cmd.append(0x00 | address)
    
    data = bytearray()
    data.append(0x00 | value)
    
    # Send out SPI message
    cs.value(0)
    spi.write(cmd)
    spi.write(data)
    cs.value(1)

###############################################################################
#
# bufferSTDIN() function to execute in parallel on second Pico RD2040 thread/processor
#
def bufferSTDIN():
    global buffer, bufferSize, bufferEcho, bufferNextIn, terminateThread
    buffer[bufferNextIn] = stdin.read(1)    # wait for/store next byte from USB serial
    if bufferEcho:                          # if echo is True ...
        print(buffer[bufferNextIn], end='') #    ... output byte to USB serial
    bufferNextIn += 1                       # bump pointer
    if bufferNextIn == bufferSize:          # ... and wrap, if necessary
        bufferNextIn = 0
#
#
# function to check if a byte is available in the buffer and if so, return it
#
def getByteBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn
    
    if bufferNextOut == bufferNextIn:           # if no unclaimed byte in buffer ...
        return ''                               #    ... return a null string
    n = bufferNextOut                           # save current pointer
    bufferNextOut += 1                          # bump pointer
    if bufferNextOut == bufferSize:             #    ... wrap, if necessary
        bufferNextOut = 0
    return (buffer[n])                          # return byte from buffer

#
# function to check if a line is available in the buffer and if so return it
# otherwise return a null string
#
# NOTE 1: a line is one or more bytes with the last byte being LF (\x0a)
#      2: a line containing only a single LF byte will also return a null string
#
def getLineBuffer():
    global buffer, bufferSize, bufferNextOut, bufferNextIn

    if bufferNextOut == bufferNextIn:           # if no unclaimed byte in buffer ...
        return ''                               #    ... RETURN a null string

    n = bufferNextOut                           # search for a LF in unclaimed bytes
    while n != bufferNextIn:
        if buffer[n] == '\x0a':                 # if a LF found ... 
            break                               #    ... exit loop ('n' pointing to LF)
        n += 1                                  # bump pointer
        if n == bufferSize:                     #    ... wrap, if necessary
            n = 0
    if (n == bufferNextIn):                     # if no LF found ...
            return ''                           #    ... RETURN a null string

    line = ''                                   # LF found in unclaimed bytes at pointer 'n'
    n += 1                                      # bump pointer past LF
    if n == bufferSize:                         #    ... wrap, if necessary
        n = 0

    while bufferNextOut != n:                   # BUILD line to RETURN until LF pointer 'n' hit
        
        if buffer[bufferNextOut] == '\x0d':     # if byte is CR
            bufferNextOut += 1                  #    bump pointer
            if bufferNextOut == bufferSize:     #    ... wrap, if necessary
                bufferNextOut = 0
            continue                            #    ignore (strip) any CR (\x0d) bytes
        
        if buffer[bufferNextOut] == '\x0a':     # if current byte is LF ...
            bufferNextOut += 1                  #    bump pointer
            if bufferNextOut == bufferSize:     #    ... wrap, if necessary
                bufferNextOut = 0
            break                               #    and exit loop, ignoring (i.e. strip) LF byte
        line = line + buffer[bufferNextOut]     # add byte to line
        bufferNextOut += 1                      # bump pointer
        if bufferNextOut == bufferSize:         #    wrap, if necessary
            bufferNextOut = 0
    return line                                 # RETURN unclaimed line of input




def printRes(Dn):
    global Rab
    Rwa = (Rab * (256 - Dn))/256
    Rwb = (Rab * Dn)/256
    
    print("Rwa = ", Rwa)
    
    print("Rwb = ", Rwb)

#
# main program begins here ...
#
# set 'inputOption' to either  one byte ‘BYTE’  OR one line ‘LINE’ at a time. Remember, ‘bufferEcho’
# determines if the background buffering function ‘bufferSTDIN’ should automatically echo each
# byte it receives from the USB serial port or not (useful when operating in line mode when the
# host computer is running a serial terminal program)
#
# start this MicroPython code running (exit Thonny with code still running) and then start a
# serial terminal program (e.g. putty, minicom or screen) on the host computer and connect
# to the Raspberry Pi Pico ...
#
#    ... start typing text and hit return.
#
#    NOTE: use Ctrl-C, Ctrl-C, Ctrl-D then Ctrl-B on in the host computer terminal program 
#           to terminate the MicroPython code running on the Pico 
#
digitalPotWrite(0)
inputOption = 'LINE'                    # get input from buffer one BYTE or LINE at a time

while True:
    bufferSTDIN()
    inputvalue = getLineBuffer()
    if inputvalue:                    # if there is...
        value_i = int(inputvalue)
        if (value_i>255):
            value_i=255
            
        digitalPotWrite(value_i)
        printRes(value_i)
        #print(value_i)
    #sleep(0.1)
    

