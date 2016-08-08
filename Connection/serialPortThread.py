from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
import serial


class SerialPortThread(MakesmithInitFuncs):
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''
    
    machineIsReadyForData = False
    
    def _write (self, message):
        message = message + " "
        message = message.encode()
        print("Sending: " + str(message))
        try:
            self.serialInstance.write(message)
        except:
            print("write issue")
        
    def getmessage (self):
        #print("Waiting for new message")
        #opens a serial connection called self.serialInstance
        
        try:
            #print("connecting")
            self.serialInstance = serial.Serial(self.data.comport, 19200, timeout = .25) #self.data.comport is the com port which is opened
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
            
            while True:
                
                
                #get new information from the machine
                try:
                    msg = self.serialInstance.readline()
                    msg = msg.decode('utf-8')
                except:
                    pass
                
                if len(msg) > 0:
                    
                    if msg == "gready\r\n":
                        self.machineIsReadyForData = True
                    else:
                        self.data.message_queue.put(msg);
                    
                        
                #send information to machine if necessary
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
                
                    