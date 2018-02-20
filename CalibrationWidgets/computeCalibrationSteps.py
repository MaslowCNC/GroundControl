'''

This is the widget which creates a frame around the calibration process providing infrastructure like the forwards and back buttons.

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty

class ComputeCalibrationSteps(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "compute calibration steps on enter"
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        print "compute calibration steps on exit"
        self.readyToMoveOn()
