'''

The widget which lets you choose the proper kinematics type for your system

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App
from   kivy.clock                                   import   Clock

class ComputeCalibrationSteps(GridLayout):
    readyToMoveOn      = ObjectProperty(None)
    setupListOfSteps   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "choose kinematics type on enter ran"
        self.setupListOfSteps()
        Clock.schedule_once(self.on_Exit, 1) #some delay is needed here to let the UI update before the next widget can be loaded
    
    def on_Exit(self, *args):
        '''
        
        This function run when the step is completed
        
        '''
        print "choose kinematics type on exit ran"
        self.readyToMoveOn()