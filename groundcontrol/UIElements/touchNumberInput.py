'''

This allows the user to touch or keyboard input a number when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
import global_variables

class TouchNumberInput(GridLayout):
    done   = ObjectProperty(None)
    
    def __init__(self,**kwargs):
        self.data = kwargs.get('data')
        super(TouchNumberInput,self).__init__(**kwargs)
        
        self.unitsBtn.text = self.data.units
        
        if global_variables._keyboard:
            global_variables._keyboard.bind(on_key_down=self.keydown_popup)
            self.bind(on_dismiss=self.ondismiss_popup)
        
    
    def keydown_popup(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == '0') or (keycode[1] =='numpad0'):
            self.addText('0')
        elif (keycode[1] == '1') or (keycode[1] =='numpad1'):
            self.addText('1')
        elif (keycode[1] == '2') or (keycode[1] =='numpad2'):
            self.addText('2')
        elif (keycode[1] == '3') or (keycode[1] =='numpad3'):
            self.addText('3')
        elif (keycode[1] == '4') or (keycode[1] =='numpad4'):
            self.addText('4')
        elif (keycode[1] == '5') or (keycode[1] =='numpad5'):
            self.addText('5')
        elif (keycode[1] == '6') or (keycode[1] =='numpad6'):
            self.addText('6')
        elif (keycode[1] == '7') or (keycode[1] =='numpad7'):
            self.addText('7')
        elif (keycode[1] == '8') or (keycode[1] =='numpad8'):
            self.addText('8')
        elif (keycode[1] == '9') or (keycode[1] =='numpad9'):
            self.addText('9')
        elif (keycode[1] == '.') or (keycode[1] =='numpaddecimal'):
            self.addText('.')
        elif (keycode[1] == 'backspace'):
            self.textInput.text = self.textInput.text[:-1]         
        elif (keycode[1] == 'enter') or (keycode[1] =='numpadenter'):
            self.done()
        elif (keycode[1] == 'escape'):     # abort entering a number, keep the old number
            self.textInput.text = ''    # clear text so it isn't converted to a number
            self.done()
        return True     # always swallow keypresses since this is a modal dialog
    
    def addText(self, text):
        '''
        
        Add a new number to what is being typed.
        
        '''
        self.textInput.text = self.textInput.text + text
    
    def forceUnitsMM(self):
        '''
        
        Forces the popup into the MM units and disables the ability to use the popup to switch units
        
        '''
        
        self.unitsBtn.text = 'MM'
        self.unitsBtn.disabled = True
    
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
    
    def ondismiss_popup(self, event):
        if global_variables._keyboard:
            global_variables._keyboard.unbind(on_key_down=self.keydown_popup)