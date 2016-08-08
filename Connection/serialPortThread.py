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
    lastTime = time.time()
    
    def _write (self, message):
        message = message.encode()
        print("Sending: ")
        print(message)
        print "time to send line: " + str(time.time() - self.lastTime)
        self.lastTime = time.time()
        try:
            self.serialInstance.write(message)
        except:
            print("write issue")
        
    def getmessage (self):
        #print("Waiting for new message")
        #opens a serial connection called self.serialInstance
        from time import sleep
        
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
                        if self.data.uploadFlag:
                            self._write("G01 X123 Y213 F100 ")
                
                #check to see if there are new commands to be sent to the machine
                if self.data.gcode_queue.empty
                    
                    