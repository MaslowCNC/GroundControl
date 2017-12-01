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
        self.measureOutChains.text          = "Now we are going to measure out the chains and reattach the sled\n\nHook the first link of each chain on the vertical tooth of each sprocket\n as shown in the picture below. Then press Calibrate Chain Lengths\n\nThe correct length of first the left and then the right chain will be measured out\n\nBe sure to keep an eye on the chains during this process to ensure that they do not become tangled\naround the sprocket. The motors are very powerful and the machine can damage itself this way\n\nOnce both chains are finished attach the sled, then press Next\n\nPressing Next will move the sled to the center of the work area"
    