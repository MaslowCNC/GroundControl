from kivy.uix.floatlayout                      import  FloatLayout
from kivy.properties                           import  ListProperty
from DataStructures.makesmithInitFuncs         import  MakesmithInitFuncs

import sys
import serial
import threading

class ConnectMenu(FloatLayout, MakesmithInitFuncs):
    
    COMports = ListProperty(("Available Ports:", "None"))
    
    def setPort(self, port):
        print "update ports"
        print port
        self.data.comport = port
    
    def connect(self, *args):
        
        self.data.config.set('Makesmith Settings', 'COMport', str(self.data.comport))
        self.data.config.write()
        
    
    def updatePorts(self, *args):
        
        portsList = ["Available Ports:"]
        
        for port in self.data.serialPort.listSerialPorts():
            portsList.append(port)
        
        if len(portsList) == 1:
            portsList.append("None")
        
        self.COMports = portsList
    
    def detectCOMports(self, *args):
        x = []
        
        altPorts = self.listSerialPorts()
        for z in altPorts:
            x.append((z,z))
        
        self.comPorts = x
