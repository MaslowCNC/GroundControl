from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from DataStructures.data          import   Data
import serial
import time
import Queue


class SerialPortThread(MakesmithInitFuncs):
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''
    
    machineIsReadyForData      = False
    lastMessageTime            = time.time()
    bufferSpace                = 256
    lengthOfLastLineStack      =  Queue.Queue()
    
    # Minimum time between lines sent to allow Arduino to cope
    # could be smaller (0.02) however larger number doesn't seem to impact performance
    MINTimePerLine = 0.05    
    
    def _write (self, message):
        message = message + ' \n'#'L' + str(len(message) + 1 + 2 + len(str(len(message))) ) + " \n"
        
        taken = time.time() - self.lastWriteTime
        if taken < self.MINTimePerLine:  # wait between sends
            # self.data.logger.writeToLog("Sleeping: " + str( taken ) + "\n")
            time.sleep (self.MINTimePerLine) # could use (taken - MINTimePerLine)
        
        self.bufferSpace       = self.bufferSpace - len(message)
        self.lengthOfLastLineStack.put(len(message))
        
        message = message.encode()
        print "Sending: " + str(message)
        
        message = message + '\n'
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
    
    def getmessage (self):
        #opens a serial connection called self.serialInstance
        
        try:
            #print("connecting")
            self.serialInstance = serial.Serial(self.data.comport, 57600, timeout = .25) #self.data.comport is the com port which is opened
        except:
            #print(self.data.comport + " is unavailable or in use")
            #self.data.message_queue.put("\n" + self.data.comport + " is unavailable or in use")
            pass
        else:
            self.data.message_queue.put("\r\nConnected on port " + self.data.comport + "\r\n")
            print("\r\nConnected on port " + self.data.comport + "\r\n")
            gcode = ""
            msg = ""
            subReadyFlag = True
            
            self.serialInstance.parity = serial.PARITY_ODD #This is something you have to do to get the connection to open properly. I have no idea why.
            self.serialInstance.close()
            self.serialInstance.open()
            self.serialInstance.close()
            self.serialInstance.parity = serial.PARITY_NONE
            self.serialInstance.open()
            
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
                if lineFromMachine == "ok\r\n":
                    if self.lengthOfLastLineStack.empty() != True:                                     #if we've sent lines to the machine
                        self.bufferSpace = self.bufferSpace + self.lengthOfLastLineStack.get_nowait()    #free up that space in the buffer
                
                
                
                
                
                                            #Write to the machine if ready
                #-------------------------------------------------------------------------------------
                
                #send any emergency instructions to the machine if there are any
                if self.data.quick_queue.empty() != True:
                    command = self.data.quick_queue.get_nowait() + " "
                    self._write(command)
                
                #send regular instructions to the machine if there are any
                if self.bufferSpace == 256:
                    
                    if self.data.gcode_queue.empty() != True:
                        command = self.data.gcode_queue.get_nowait() + " "
                        self._write(command)
                
                #Send the next line of gcode to the machine if we're running a program
                if self.bufferSpace == 256:#> len(self.data.gcode[self.data.gcodeIndex]):
                    if self.data.uploadFlag:
                        self._write(self.data.gcode[self.data.gcodeIndex])
                        
                        #increment gcode index
                        if self.data.gcodeIndex + 1 < len(self.data.gcode):
                            self.data.gcodeIndex = self.data.gcodeIndex + 1
                        else:
                            self.data.uploadFlag = 0
                            self.data.gcodeIndex = 0
                            print "Gcode Ended"
                
                
                
                
                
                
                                            #Check for serial connection loss
                #-------------------------------------------------------------------------------------
                if time.time() - self.lastMessageTime > 2:
                    print "connection lost"
                    self.data.message_queue.put("Connection Lost")
                    if self.data.uploadFlag:
                        self.data.message_queue.put("Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.")
                    self.data.connectionStatus = 0
                    self.serialInstance.close()
                    return
                    