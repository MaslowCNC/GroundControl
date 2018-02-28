'''

The intro page which explains the calibration process

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class Intro(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "intro on enter"
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        print "intro on exit"
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', 'Top')
        self.readyToMoveOn()
