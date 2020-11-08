from   kivy.uix.gridlayout                  import  GridLayout
from   kivy.properties                      import   ObjectProperty
from   kivy.app                             import   App

class MeasureOneChain(GridLayout):
    '''
    
    Provides a standard interface for measuring the distance between the motors. Assumes that both motors are in position zero at the begining
    
    '''
    data                         =   ObjectProperty(None)
    direction = 'L'
    
    def setDirection(self, direction):
        self.direction = direction
        
        if self.direction == 'L':
            self.mainText.text = "Now that we know the distance between the motors we can check the tolerances on the chains.\n\nExtend the left chain, hook it on the oposit motor, then press measure"
        else:
            self.mainText.text = "Now again with the right chain (the miror or what we did before).\n\nExtend the right chain, hook it on the oposit motor, then press measure"
    
    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def extend(self):
        dist = self.data.motorsDist + 25 #extend a little extra to make it easy to hook on
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 " + self.direction + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def measure(self):
        
        self.pullChainTight()
        
        #requeust a measurement
        self.data.gcode_queue.put("B10 " + self.direction)
        
    
    def readMotorSpacing(self, dist):
        dist = dist - 2*6.35                                #subtract off the extra two links

        print("Read motor spacing: " + str(dist))
        
        #put some slack in the chain
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 " + self.direction + "10 ")
        self.data.gcode_queue.put("G90 ")
        
        if self.direction == 'L':
            self.data.leftChainMeasurement = dist
        else:
            self.data.rightChainMeasurement = dist
        
        self.readyToMoveOn()
    
    def pullChainTight(self):
        #pull the left chain tight
        self.data.gcode_queue.put("B11 S255 T3 " + self.direction)
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
        self.data.measureRequest = self.readMotorSpacing
        
        self.originalChainOverSproketDir = self.data.config.get('Advanced Settings', 'chainOverSprocket')
        
        #pretend we are in the "Top" configuration during this step
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', 'Top')
        
        #set the threshold for warning that the machine is off target to 200mm esentially turning it off. We dont' want this to trigger when pulling the chain tight
        self.data.gcode_queue.put("$42=200 ")
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        
        #Restore original chain over sprocket direction
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', self.originalChainOverSproketDir)
        #restore all settings to the values stored in the current settings file 
        self.data.gcode_queue.put("$$ ")
        
