from groundcontrol.data_structures.makesmithInitFuncs         import   MakesmithInitFuncs
from groundcontrol.data_structures.data          import   Data
import serial
import time
from collections import deque


class SerialPortThread(MakesmithInitFuncs):
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''
    
    machineIsReadyForData      = False # Tracks whether last command was acked
    lastWriteTime              = time.time()
    bufferSize                 = 126                #The total size of the arduino buffer
    bufferSpace                = bufferSize         #The amount of space currently available in the buffer
    lengthOfLastLineStack      =  deque()
    
    # Minimum time between lines sent to allow Arduino to cope
    # could be smaller (0.02) however larger number doesn't seem to impact performance
    MINTimePerLine = 0.05    
    
    def _write (self, message, isQuickCommand = False):
        #message = message + 'L' + str(len(message) + 1 + 2 + len(str(len(message))) )
        
        taken = time.time() - self.lastWriteTime
        if taken < self.MINTimePerLine:  # wait between sends
            # self.data.logger.writeToLog("Sleeping: " + str( taken ) + "\n")
            time.sleep (self.MINTimePerLine) # could use (taken - MINTimePerLine)
        
        message = message.encode()
        print("Sending: " + str(message))
        
        message = message + '\n'
        
        self.bufferSpace       = self.bufferSpace - len(message)        #shrink the available buffer space by the length of the line
        
        self.machineIsReadyForData = False
        
        #if this is a quick message sent as soon as the button is pressed (like stop) then put it on the right side of the queue
        #because it is the first message sent, otherwise put it at the end (left) because it is the last message sent
        if isQuickCommand:
            if message[0] == '!':
                #if we've just sent a stop command, the buffer is now empty on the arduino side
                self.lengthOfLastLineStack.clear()
                self.bufferSpace = self.bufferSize - len(message)
                self.lengthOfLastLineStack.append(len(message)) 
            else:
                self.lengthOfLastLineStack.append(len(message))
        else:
            self.lengthOfLastLineStack.appendleft(len(message))
        
        
        message = message.encode()
        try:
            self.serialInstance.write(message)
            self.data.logger.writeToLog("Sent: " + str(message))
        except:
            print("write issue")
            self.data.logger.writeToLog("Send FAILED: " + str(message))
    
        self.lastWriteTime = time.time()

    def _getFirmwareVersion(self):
        self.data.gcode_queue.put('B05 ')
    
    def _setupMachineUnits(self):
        if self.data.units == "INCHES":
            self.data.gcode_queue.put('G20 ')
        else:
            self.data.gcode_queue.put('G21 ')
    
    def sendNextLine(self):
        '''
            Sends the next line of gcode to the machine
        '''
        
        if self.data.uploadFlag:
            self._write(self.data.gcode[self.data.gcodeIndex])
            
            #increment gcode index
            if self.data.gcodeIndex + 1 < len(self.data.gcode):
                self.data.gcodeIndex = self.data.gcodeIndex + 1
            else:
                self.data.uploadFlag = 0
                self.data.gcodeIndex = 0
                print("Gcode Ended")
    
    def getmessage (self):
        #opens a serial connection called self.serialInstance
        
        #check for serial version being > 3
        if float(serial.VERSION[0]) < 3:
            self.data.message_queue.put("Pyserial version 3.x is needed, version " + serial.VERSION + " is installed")
        
        weAreBufferingLines = bool(int(self.data.config.get('Maslow Settings', "bufferOn")))
        
        try:
            #print("connecting")
            self.serialInstance = serial.Serial(self.data.comport, 57600, timeout = .25) #self.data.comport is the com port which is opened
        except:
            #print(self.data.comport + " is unavailable or in use")
            #self.data.message_queue.put("\n" + self.data.comport + " is unavailable or in use")
            pass
        else:
            self.data.message_queue.put("\r\nConnected on port " + self.data.comport + "\r\n")
            print(("\r\nConnected on port " + self.data.comport + "\r\n"))
            gcode = ""
            msg = ""
            subReadyFlag = True
            
            
            if self.serialInstance.isOpen(): 
                self.serialInstance.close()
            
            self.serialInstance.open()
            
            # reset Arduino boards by toggling DTR signal
            self.serialInstance.dtr = False
            self.serialInstance.dtr = True
            
            # reset non-Arduino boards by sending 
            self._write(b'\x18') # ctrl-X
            
            #print "port open?:"
            #print self.serialInstance.isOpen()
            self.lastMessageTime = time.time()
            self.data.connectionStatus = 1
            
            self._getFirmwareVersion()
            self._setupMachineUnits()
            
            while True:
                
                
                                        #Read serial line from machine if available
                #-------------------------------------------------------------------------------------
                lineFromMachine = ""
                
                try:
                    if self.serialInstance.in_waiting > 0:
                        lineFromMachine = self.serialInstance.readline()
                        self.lastMessageTime = time.time()
                        self.data.message_queue.put(lineFromMachine)
                except:
                    pass
                
                #Check if a line has been completed
                if lineFromMachine == "ok\r\n" or (len(lineFromMachine) >= 6 and lineFromMachine[0:6] == "error:"):
                    self.machineIsReadyForData = True
                    if bool(self.lengthOfLastLineStack) is True:                                     #if we've sent lines to the machine
                        self.bufferSpace = self.bufferSpace + self.lengthOfLastLineStack.pop()    #free up that space in the buffer
                
                
                
                                            #Write to the machine if ready
                #-------------------------------------------------------------------------------------
                
                #send any emergency instructions to the machine if there are any
                if self.data.quick_queue.empty() != True:
                    command = self.data.quick_queue.get_nowait()
                    self._write(command, True)
                
                #send regular instructions to the machine if there are any
                if self.bufferSpace == self.bufferSize and self.machineIsReadyForData:
                    if self.data.gcode_queue.empty() != True:
                        command = self.data.gcode_queue.get_nowait() + " "
                        self._write(command)
                
                #Send the next line of gcode to the machine if we're running a program. Will send lines to buffer if there is space
                #and the feature is turned on
                if weAreBufferingLines:
                    try:
                        if self.bufferSpace > len(self.data.gcode[self.data.gcodeIndex]): #if there is space in the buffer keep sending lines
                            self.sendNextLine()
                    except IndexError:
                        print("index error when reading gcode") #we don't want the whole serial thread to close if the gcode can't be sent because of an index error (file deleted...etc)
                else:
                    if self.bufferSpace == self.bufferSize and self.machineIsReadyForData: #if the receive buffer is empty and the machine has acked the last line complete
                        self.sendNextLine()
                
                
                                            #Check for serial connection loss
                #-------------------------------------------------------------------------------------
                if time.time() - self.lastMessageTime > 2:
                    print("Connection Timed Out")
                    self.data.message_queue.put("Connection Timed Out\n")
                    if self.data.uploadFlag:
                        self.data.message_queue.put("Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.")
                    else:
                        self.data.message_queue.put("It is possible that the serial port selected is not the one used by the Maslow's Arduino,\nor that the firmware is not loaded on the Arduino.")
                    self.data.connectionStatus = 0
                    self.serialInstance.close()
                    return
                
                # Sleep between passes to save CPU
                time.sleep(.001)
                    