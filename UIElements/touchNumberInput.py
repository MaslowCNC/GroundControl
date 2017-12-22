'''

This allows the user to touch or keyboard input a number when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty

class TouchNumberInput(GridLayout):
    done   = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        self.data = kwargs.get('data')
        super(TouchNumberInput,self).__init__(**kwargs)
        
        self.unitsBtn.text = self.data.units
    
    def addText(self, text):
        '''
        
        Add a new number to what is being typed.
        
        '''
        self.textInput.text = self.textInput.text + text
    
    def switchUnits(self):
        '''
        
        Switch the units of the entered number
        
        '''
        if self.data.units == "INCHES":
            self.data.units = "MM"
            self.unitsBtn.text = 'MM'
        else:
            self.data.units = "INCHES"
            self.unitsBtn.text = 'INCHES'