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
        print "choose kinematics type on enter ran"
    
    def setKinematicsTypeQuad(self):
        '''
        
        Write into the settings that the kinematics type is quadrilateral
        
        '''
        print "set quad"
        App.get_running_app().data.config.set('Advanced Settings', 'kinematicsType', 'Quadrilateral')
        App.get_running_app().data.config.write()
        self.on_Exit()
    
    def setKinematicsTypeTri(self):
        '''
        
        Write into the settings that the kinematics type is triangular
        
        '''
        print "set tri"
        App.get_running_app().data.config.set('Advanced Settings', 'kinematicsType', 'Triangular')
        App.get_running_app().data.config.write()
        self.on_Exit()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        print "choose kinematics type on exit ran"
        self.readyToMoveOn()