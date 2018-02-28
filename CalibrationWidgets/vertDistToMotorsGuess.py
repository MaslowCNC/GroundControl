'''

A template for creating a new calibration step widget

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   UIElements.touchNumberInput                  import   TouchNumberInput
from   kivy.uix.popup                               import   Popup
from   kivy.app                                     import   App
import global_variables

class VertDistToMotorsGuess(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
    
    def textInputPopup(self, target):
        self.targetWidget = target

        self.popupContent = TouchNumberInput(done=self.dismiss_popup, data = self.data)
        self._popup = Popup(title="Set distance to move chain", content=self.popupContent,
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
    
    def dismiss_popup(self):
        try:
            tempfloat = float(self.popupContent.textInput.text)
            self.targetWidget.text = str(tempfloat)  # Update displayed text using standard numeric format
            #self.distText.text = "Dist (" + self.data.units + "):"
        except:
            pass  # If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        
        try:
            dist = float(self.enterMeasurement.text)
            self.data.config.set('Maslow Settings', 'motorOffsetY', str(dist))
            self.readyToMoveOn()
        except:
            self.data.message_queue.put("Message: Couldn't convert that to a number...")
        
        