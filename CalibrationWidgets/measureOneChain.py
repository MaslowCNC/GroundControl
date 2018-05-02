from   kivy.uix.gridlayout                  import  GridLayout
from   kivy.properties                      import   ObjectProperty
from   UIElements.touchNumberInput          import   TouchNumberInput
from   kivy.uix.popup                       import   Popup
from   kivy.app                             import   App
import global_variables

class MeasureOneChain(GridLayout, direction):
    '''
    
    Provides a standard interface for measuring the distance between the motors. Assumes that both motors are in position zero at the begining
    
    '''
    data                         =   ObjectProperty(None)
    
    
    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def extend(self):
        dist = self.data.motorsDist + 25 #extend a little extra to make it easy to hook on
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 " + direction + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def measure(self):
        
        self.pullChainTight()
        
        self.data.gcode_queue.put("B10 " + direction)
        print "measured chain as"
    
    def readMotorSpacing(self, dist):
        dist = dist - 2*6.35                                #subtract off the extra two links

        print "Read motor spacing: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorSpacingX', str(dist))
        
        #put some slack in the chain
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 " + direction + "10 ")
        self.data.gcode_queue.put("G90 ")
        
        self.readyToMoveOn()
    
    def pullChainTight(self):
        #pull the left chain tight
        self.data.gcode_queue.put("B11 S50 T3 ")
    
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
        
