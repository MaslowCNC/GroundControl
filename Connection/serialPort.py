
class SerialPort():
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''

    def __init__( self, message_queue, gcode_queue, mainwindow, comport, quick_queue):
        self.message_queue = message_queue
        self.gcode_queue = gcode_queue
        self.quick_queue = quick_queue
        self.mainwindow = mainwindow
        self.comport = comport
        
    def getmessage (self):
        print("Waiting for new message")
        #opens a serial connection called serialCAN
        from time import sleep
        
        try:
            print("connecting")
            serialCAN = serial.Serial(self.comport, 9600, timeout = .25) #self.comport is the com port which is opened
        except:
            print(self.comport + "is unavailable or in use")
            self.message_queue.put("\n" + self.comport + " is unavailable or in use")
        else:
            self.message_queue.put("\r\nConnected on port " + self.comport + "\r\n")
            gcode = ""
            msg = ""
            subReadyFlag = True
            
            serialCAN.parity = serial.PARITY_ODD #This is something you have to do to get the connection to open properly. I have no idea why.
            serialCAN.close()
            serialCAN.open()
            serialCAN.close()
            serialCAN.parity = serial.PARITY_NONE
            serialCAN.open()
            
            print "port open?:"
            print serialCAN.isOpen()
            
            while True:
                
                try:
                    msg = serialCAN.readline() #rand.random()
                except:
                    pass
                try:
                    msg = msg.decode('utf-8')
                except:
                    pass
                    
                if len(msg) > 0:
                    
                    
                    if msg == "gready\r\n":
                        subReadyFlag = True
                        if self.gcode_queue.qsize() >= 1:
                            msg = ""
                    
                    if msg == "Clear Buffer\r\n":
                        print("buffer cleared")
                        while self.gcode_queue.empty() != True:
                            gcode = self.gcode_queue.get_nowait()
                        gcode = ""
                        msg = ""
                    
                    self.message_queue.put(msg)
                    
                msg = ""
                
                if self.gcode_queue.empty() != True and len(gcode) is 0:
                        gcode = self.gcode_queue.get_nowait()
                        gcode = gcode + " "
                if self.quick_queue.empty() != True:
                        qcode = self.quick_queue.get_nowait()
                        qcode = qcode.encode()
                        if qcode == b'Reconnect': #this tells the machine serial thread to close the serial connection
                            qcode = ""
                            print("Attempting to Re-establish connection")
                            serialCAN.close() #closes the serial port
                            sleep(.25)
                            try:
                                serialCAN.open()
                            except:
                                return -1
                        else:
                            try:
                                serialCAN.write(qcode)
                            except:
                                print("write issue 2")
                if len(gcode) > 0 and subReadyFlag is True:
                    gcode = gcode.encode()
                    print("Sending: ")
                    print(gcode)
                    try:
                        serialCAN.write(gcode)
                        gcode = ""  
                    except:
                        print("write issue")
                    subReadyFlag = False
                else:
                    pass
