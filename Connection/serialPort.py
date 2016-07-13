from kivy.properties                           import  ListProperty
from kivy.clock                                import  Clock
from DataStructures.makesmithInitFuncs         import  MakesmithInitFuncs
from Connection.serialPortThread               import  SerialPortThread

import sys
import serial
import threading

class SerialPort(MakesmithInitFuncs):
    '''
    
    The SerialPort is an object which manages communication with the device over the serial port.
    
    The actual connection is run in a separate thread by an instance of a SerialPortThread object.
    
    '''
    
    
    COMports = ListProperty(("Available Ports:", "None"))
    
    def __init__(self):
        '''
        
        Runs on creation, schedules the software to attempt to connect to the machine
        
        '''
        Clock.schedule_interval(self.recieveMessage, 2)
    
    def setPort(self, port):
        '''
        
        Defines which port the machine is attached to
        
        '''
        print "update ports"
        print port
        self.data.comport = port
    
    def connect(self, *args):
        '''
        
        Forces the software to begin trying to connect on the new port.
        
        This function may not be necessary, but it should stay in because it simplifies the user experience.
        
        '''
        self.data.config.set('Makesmith Settings', 'COMport', str(self.data.comport))
        self.data.config.write()
    
    def updatePorts(self, *args):
        '''
        
        Talks to the OS and determines which devices are available on which ports.
        
        '''
        
        portsList = ["Available Ports:"]
        
        for port in self.listSerialPorts():
            portsList.append(port)
        
        if len(portsList) == 1:
            portsList.append("None")
        
        self.COMports = portsList
    
    '''
    
    Serial Connection Functions
    
    '''
    
    def recieveMessage(self, *args):
        #This function opens the thread which handles the input from the serial port
        #It only needs to be run once, it is run by connecting to the machine
        
        #self.data.message_queue is the queue which handles passing CAN messages between threads
        x = SerialPortThread()
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
