from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from Connection.serialPort                     import   SerialPort

class NonVisibleWidgets(MakesmithInitFuncs):
    serialPort = SerialPort()
    
    def setUpData(self, data):
        self.data = data
        print "Initialized: " + str(self)
        
        data.serialPort = self.serialPort #add the serial port widget to the data object
        self.serialPort.setUpData(data)