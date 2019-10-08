from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from Connection.serialPort                     import   SerialPort

class NonVisibleWidgets(MakesmithInitFuncs):
    '''
    
    NonVisibleWidgets is a home for widgets which do not have a visible representation like
    the serial connection, but which still need to be tied in to the rest of the program.
    
    '''
    
    serialPort = SerialPort()
    
    def setUpData(self, data):
        '''
        
        The setUpData function is called when a widget is first created to give that widget access
        to the global data object. This should be replaced with a supper classed version of the __init__
        function. 
        
        '''
        
        self.data = data
        #print("Initialized: " + str(self))
        
        data.serialPort = self.serialPort #add the serial port widget to the data object
        self.serialPort.setUpData(data)