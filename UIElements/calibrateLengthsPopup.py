'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   kivy.uix.popup                            import   Popup
from   UIElements.setSprocketsVertical           import   SetSprocketsVertical

class CalibrateLengthsPopup(GridLayout):
    done   = ObjectProperty(None)
    
    
    def establishDataConnection(self, data):
        '''
        
        Sets up the data connection between this popup and the shared data object
        
        '''
        self.data = data
        self.setSprocketsVertical.data = data
        self.setSprocketsVertical.carousel = self.carousel
    
    def stop(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def calibrateChainLengths(self):
        self.data.gcode_queue.put("B02 ")
        
    