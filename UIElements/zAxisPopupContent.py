'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   UIElements.touchNumberInput               import   TouchNumberInput
from   kivy.uix.popup                            import   Popup
import global_variables

class ZAxisPopupContent(GridLayout):
    done   = ObjectProperty(None)
    
    def initialize(self, zStepSizeVal):
        '''
        
        Initialize the z-axis popup
        
        '''
        self.unitsBtn.text = self.data.units
        self.distBtn.text  = str(zStepSizeVal)
    
    def setDist(self):
        self.popupContent = TouchNumberInput(done=self.dismiss_popup)
        self._popup = Popup(title="Change increment size of machine movement", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        if global_variables._keyboard:
            global_variables._keyboard.bind(on_key_down=self.keydown_popup)
            self._popup.bind(on_dismiss=self.ondismiss_popup)

    def ondismiss_popup(self, event):
        if global_variables._keyboard:
            global_variables._keyboard.unbind(on_key_down=self.keydown_popup)

    def keydown_popup(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == '0') or (keycode[1] =='numpad0'):
            self.popupContent.addText('0')
        elif (keycode[1] == '1') or (keycode[1] =='numpad1'):
            self.popupContent.addText('1')
        elif (keycode[1] == '2') or (keycode[1] =='numpad2'):
            self.popupContent.addText('2')
        elif (keycode[1] == '3') or (keycode[1] =='numpad3'):
            self.popupContent.addText('3')
        elif (keycode[1] == '4') or (keycode[1] =='numpad4'):
            self.popupContent.addText('4')
        elif (keycode[1] == '5') or (keycode[1] =='numpad5'):
            self.popupContent.addText('5')
        elif (keycode[1] == '6') or (keycode[1] =='numpad6'):
            self.popupContent.addText('6')
        elif (keycode[1] == '7') or (keycode[1] =='numpad7'):
            self.popupContent.addText('7')
        elif (keycode[1] == '8') or (keycode[1] =='numpad8'):
            self.popupContent.addText('8')
        elif (keycode[1] == '9') or (keycode[1] =='numpad9'):
            self.popupContent.addText('9')
        elif (keycode[1] == '.') or (keycode[1] =='numpaddecimal'):
            self.popupContent.addText('.')
        elif (keycode[1] == 'backspace'):
            self.popupContent.textInput.text = self.popupContent.textInput.text[:-1]         
        elif (keycode[1] == 'enter') or (keycode[1] =='numpadenter'):
            self.popupContent.done()
        elif (keycode[1] == 'escape'):     # abort entering a number, keep the old number
            self.popupContent.textInput.text = ''    # clear text so it isn't converted to a number
            self.popupContent.done()
        return True     # always swallow keypresses since this is a modal dialog
    
    def units(self):
        '''
        
        Toggle the machine units.
        
        '''
        if self.data.units == "INCHES":
            self.data.units = "MM"
            self.distBtn.text = str(25*float(self.distBtn.text))
        else:
            self.data.units = "INCHES"
            
            self.distBtn.text = str(float(self.distBtn.text)/25)
        
        self.unitsBtn.text = self.data.units
    
    def zIn(self):
        '''
        
        Move the z-axis in
        
        '''
        self.data.gcode_queue.put("G91 G00 Z" + str(-1*float(self.distBtn.text)) + " G90 ")
    
    def zOut(self):
        '''
        
        Move the z-axis out
        
        '''
        self.data.gcode_queue.put("G91 G00 Z" + str(self.distBtn.text) + " G90 ")
    
    def zero(self):
        '''
        
        Define the z-axis to be currently at height 0
        
        '''
        self.data.gcode_queue.put("G10 Z0 ")
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up to enter distance information
        
        '''
        try:
            float(self.popupContent.textInput.text)
            self.distBtn.text = self.popupContent.textInput.text
        except:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()
