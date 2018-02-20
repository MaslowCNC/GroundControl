'''

A template for creating a new calibration step widget

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty

class ChooseKinematicsType(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "choose kinematics type on enter ran"
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        print "choose kinematics type on exit ran"