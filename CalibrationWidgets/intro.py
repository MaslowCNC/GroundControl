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
        
        self.data = App.get_running_app().data
        
        if self.data.connectionStatus == False:
            self.data.message_queue.put("Message: The calibration process requres the machine to be connected. To connect to the machine choose Actions -> Ports and select the same port used to install the firmware")
    
    def finished(self):
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        
        pass
