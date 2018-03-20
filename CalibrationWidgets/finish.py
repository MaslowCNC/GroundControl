'''

A template for creating a new calibration step widget

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty

class Finish(GridLayout):
    done   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        pass
    
    def closePopup(self):
        self.done()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        self.readyToMoveOn()