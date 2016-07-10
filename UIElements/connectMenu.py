from kivy.uix.floatlayout                      import  FloatLayout
from kivy.properties                           import  ListProperty

from Connection.serialPort                     import  SerialPort
from DataStructures.makesmithInitFuncs         import  MakesmithInitFuncs

import sys
import serial
import threading

class ConnectMenu(FloatLayout, MakesmithInitFuncs):
    
    COMports = ListProperty(("Available Ports:", "None"))
    comPort = ""
    
    def setPort(self, port):
        print "update ports"
        print port
        self.comPort = port
    
    def connect(self, *args):
        print "connect pressed"
        
        self.recieveMessage()
    
    def updatePorts(self, *args):
        
        portsList = ["Available Ports:"]
        
        for port in self.listSerialPorts():
            portsList.append(port)
        
        if len(portsList) == 1:
            portsList.append("None")
        
        self.COMports = portsList
    
    def ports(self):
        print "ports"
        self.data.gcode_queue.put("test gcode");
    
        '''
    
    Serial Connection Functions
    
    '''
    
    def recieveMessage(self):
        #This function opens the thread which handles the input from the serial port
        #It only needs to be run once, it is run by connecting to the machine
        
        print("Starting Second Thread")
        #self.data.message_queue is the queue which handles passing CAN messages between threads
        x = SerialPort()
        x.setUpData(self.data)
        self.th=threading.Thread(target=x.getmessage)
        self.th.daemon = True
        self.th.start()
    
    def listSerialPorts(self):
        #Detects all the devices connected to the computer. Returns them as an array.
        import glob
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
            except (ValueError):
                print("Port find error")
        return result
    
    def detectCOMports(self, *args):
        x = []
        
        altPorts = self.listSerialPorts()
        for z in altPorts:
            x.append((z,z))
        
        self.comPorts = x
