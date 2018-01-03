from kivy.uix.floatlayout                      import  FloatLayout
from kivy.properties                           import  ListProperty
from DataStructures.makesmithInitFuncs         import  MakesmithInitFuncs

import sys
import glob
import serial
import threading
import serial.tools.list_ports

class ConnectMenu(FloatLayout, MakesmithInitFuncs):
    
    COMports = ListProperty(("Available Ports:", "None"))
    
    def setPort(self, port):
        print "update ports"
        print port
        self.data.comport = port
    
    def connect(self, *args):
        
        self.data.config.set('Maslow Settings', 'COMport', str(self.data.comport))
        self.data.config.write()
        
        #close the parent popup
        self.parentWidget.close()
        
    
    def updatePorts(self, *args):
        
        portsList = ["Available Ports:"]
        
        if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            sysports = glob.glob('/dev/tty[A-Za-z]*')
            for port in sysports:
                portsList.append(port)

        elif sys.platform.startswith('darwin'):
            sysports = glob.glob('/dev/tty.*')
            for port in sysports:
                portsList.append(port)

        elif sys.platform.startswith('win'):
            for port in self.listSerialPorts():
                portsList.append(port)
        
        else:
            raise EnvironmentError('Unsupported platform - can\'t find serial ports')

        if len(portsList) == 1:
            portsList.append("None")
        
        self.COMports = portsList
    

    def listSerialPorts(self):
        #Detects all the devices connected to the computer. Returns them as an array.
        # import glob
        # Only called for Windows platforms
        ports = []
        if sys.platform.startswith('win'): 
            list = serial.tools.list_ports.comports()
            for element in list:
                ports.append(element.device)    

        else:
            raise EnvironmentError('Windows port search error')

        return ports
        #result = []
        #for port in ports:
        #    try:
        #        s = serial.Serial(port)
        #        s.close()
        #        print ("Port " + port)
        #        result.append(port)
        #    except (OSError, serial.SerialException):
        #        pass
        #    except (ValueError):
        #        print("Port find error")
        #return result
    
