'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   kivy.uix.popup                            import   Popup
from   UIElements.setSprocketsVertical           import   SetSprocketsVertical
from   UIElements.measureOutChains               import   MeasureOutChains

class CalibrateLengthsPopup(GridLayout):
    done   = ObjectProperty(None)
    
    
    def establishDataConnection(self, data):
        '''
        
        Sets up the data connection between this popup and the shared data object
        
        '''
        self.data = data
        
        self.setSprocketsVertical.data      =  data
        self.setSprocketsVertical.carousel  =  self.carousel
        
        self.measureOutChains.data          =  data
        self.measureOutChains.carousel      =  self.carousel
    