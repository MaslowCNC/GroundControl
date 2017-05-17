from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
import serial
import time


class SerialPortThread(MakesmithInitFuncs):
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''
    
    machineIsReadyForData = False
    lastMessageTime       = time.time()
    
    def _write (self, message):
        message = message + " \n"
        message = message.encode()
        print("Sending: " + str(message))
        try:
            self.serialInstance.write(message)
        except:
            print("write issue")

    def _getFirmwareVersion(self):
        self.data.gcode_queue.put('B05 ')
    
    def _setupMachineUnits(self):
        if self.data.units == "INCHES":
            self.data.gcode_queue.put('G20 ')
        else:
            self.data.gcode_queue.put('G21 ')
    
    def _checkBufferSize(self, msg):
        '''
        
        Check if the machine has enough room in it's buffer for more gcode
        
        '''
        
        valz = msg.split(",")
        
        try:
            print int(valz[2][0:-3])
            if int(valz[2][0:-3]) > 127 - len(self.data.gcode[self.data.gcodeIndex]):             #if there is space in the arduino buffer
                self.machineIsReadyForData = True
        except:
            self.data.uploadFlag = 0
            self.data.gcodeIndex = 0
            print "Gcode Ended"
    
    def getmessage (self):
        #print("Waiting for new message")
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
                
                #get any messages from the machine
                try:
                    msg = self.serialInstance.readline()
                    msg = msg.decode('utf-8')
                except:
                    pass
                if len(msg) > 0:
                    self.lastMessageTime = time.time()
                    if msg == "ok\r\n":
                        pass
                        #self.machineIsReadyForData = True
                    else:
                        if msg[0] == "[":
                            self._checkBufferSize(msg)
                        self.data.message_queue.put(msg)
                    
                #send any emergency instructions to the machine if there are any
                if self.data.quick_queue.empty() != True:
                    command = self.data.quick_queue.get_nowait() + " "
                    self._write(command)
                    
                #send gcode to machine if it is ready
                if self.machineIsReadyForData:
                    if self.data.gcode_queue.empty() != True:
                        gcode = self.data.gcode_queue.get_nowait() + " "
                        self._write(gcode)
                        self.machineIsReadyForData = False
                        
                    elif self.data.uploadFlag:
                        try:
                            self._write(self.data.gcode[self.data.gcodeIndex])
                            self.data.gcodeIndex = self.data.gcodeIndex + 1
                            self.machineIsReadyForData = False
                        except:
                            self.data.uploadFlag = 0
                            print "Gcode Ended"
                
                #check for serial connection loss
                if time.time() - self.lastMessageTime > 2:
                    print "connection lost"
                    self.data.message_queue.put("Connection Lost")
                    if self.data.uploadFlag:
                        self.data.message_queue.put("Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.")
                    self.data.connectionStatus = 0
                    self.serialInstance.close()
                    return
                msg = ""
                    