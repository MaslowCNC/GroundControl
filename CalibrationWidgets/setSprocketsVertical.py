from   kivy.uix.gridlayout                import  GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.app                           import   App

class SetSprocketsVertical(GridLayout):
    '''

    Provides a standard interface for making both sprockets point vertically

    '''
    data            = ObjectProperty(None)
    readyToMoveOn   = ObjectProperty(None)
    
    leftChainLength = 0
    rightchainLength = 0

    def LeftCW360(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/1.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCW360(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/1.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCCW360(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/1.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCCW360(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/1.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCW(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/360.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCCW(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/360.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCW(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/360.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCCW(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/360.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCW5(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/72.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCCW5(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/72.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCW5(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/72.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCCW5(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/72.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCWpoint1(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/3600.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def LeftCCWpoint1(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/3600.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCWpoint1(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/3600.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")

    def RightCCWpoint1(self):
        degValue = float(self.data.config.get('Advanced Settings',"gearTeeth"))*float(self.data.config.get('Advanced Settings',"chainPitch"))/3600.0;
        self.data.gcode_queue.put("G91 ")
        if self.data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            self.data.gcode_queue.put("B09 R"+str(degValue)+" ")
        else:
            self.data.gcode_queue.put("B09 R-"+str(degValue)+" ")
        self.data.gcode_queue.put("G90 ")
    
    def setVerticalAutomatic(self):
        '''
        
        This function will do it's best to set the sprockets vertical automatically
        
        '''
        
        #set the call back for the measurement
        self.data.measureRequest = self.getLeftChainLength
        #request a measurement
        self.data.gcode_queue.put("B10 L")
    
    def getLeftChainLength(self, dist):
        '''
        
        Get the left chain length
        
        '''
        self.leftChainLength = dist
        #set the call back for the measurement
        self.data.measureRequest = self.getRightChainLength
        #request a measurement
        self.data.gcode_queue.put("B10 R")
    
    def getRightChainLength(self, dist):
        '''
        
        Get the right chain length
        
        '''
        self.rightChainLength = dist
        self.moveToVertical()
    
    def moveToVertical(self):
        '''
        
        Move the sprockets to vertical
        
        '''
        
        print "Current chain lengths:"
        print self.leftChainLength
        print self.rightChainLength
        
        chainPitch = float(self.data.config.get('Advanced Settings', 'chainPitch'))
        gearTeeth  = float(self.data.config.get('Advanced Settings', 'gearTeeth'))
        
        distPerRotation = chainPitch*gearTeeth
        
        print "Rotations remainder:"
        distL = (-1*(self.leftChainLength%distPerRotation))
        distR = (-1*(self.rightChainLength%distPerRotation))
        
        print distL
        print distR
        
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L"+str(distL)+" ")
        self.data.gcode_queue.put("B09 R"+str(distR)+" ")
        self.data.gcode_queue.put("G90 ")
    
    def setZero(self):
        #mark that the sprockets are straight up
        self.data.gcode_queue.put("B06 L0 R0 ");
        self.readyToMoveOn()
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        pass
        