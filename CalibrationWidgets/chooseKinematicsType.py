'''

The widget which lets you choose the proper kinematics type for your system

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class ChooseKinematicsType(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        
    
    def setKinematicsTypeQuad(self):
        '''
        
        Write into the settings that the kinematics type is quadrilateral
        
        '''
        
        App.get_running_app().data.config.set('Advanced Settings', 'kinematicsType', 'Quadrilateral')
        self.on_Exit()
    
    def setKinematicsTypeTri(self):
        '''
        
        Write into the settings that the kinematics type is triangular
        
        '''
        
        App.get_running_app().data.config.set('Advanced Settings', 'kinematicsType', 'Triangular')
        self.on_Exit()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        
        self.readyToMoveOn()