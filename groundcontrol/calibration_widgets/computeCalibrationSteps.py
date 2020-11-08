'''

The widget which lets you choose the proper kinematics type for your system

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.clock                                   import   Clock

class ComputeCalibrationSteps(GridLayout):
    readyToMoveOn      = ObjectProperty(None)
    setupListOfSteps   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        
        self.setupListOfSteps()
        Clock.schedule_once(self.loadNextStep, 5) #some delay is needed here to let the UI update before the next widget can be loaded
    
    def loadNextStep(self, *args):
        self.readyToMoveOn()
    
    def on_Exit(self, *args):
        '''
        
        This function run when the step is completed
        
        '''
        pass