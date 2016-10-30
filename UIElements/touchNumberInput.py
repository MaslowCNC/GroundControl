'''

This allows the user to touch or keyboard input a number when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty

class TouchNumberInput(GridLayout):
    done   = ObjectProperty(None)
    
    def addText(self, text):
        self.textInput.text = self.textInput.text + text