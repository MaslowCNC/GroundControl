from   kivy.uix.gridlayout                  import  GridLayout
from   kivy.properties                      import   ObjectProperty
from   UIElements.touchNumberInput          import   TouchNumberInput
from   kivy.uix.popup                       import   Popup
from   kivy.app                             import   App
import global_variables

class MeasureDistBetweenMotors(GridLayout):
    '''
    
    Provides a standard interface for measuring the distance between the motors. Assumes that both motors are in position zero at the begining
    
    '''
    data                         =   ObjectProperty(None)
    
    def textInputPopup(self, target):
        self.targetWidget = target

        self.popupContent = TouchNumberInput(done=self.dismiss_popup, data = self.data)
        self.popupContent.forceUnitsMM()
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
    
    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def extend(self):
        dist = float(self.distToMove.text)
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def retract(self):
        dist = float(self.distToMove.text)
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L" + str(-1*dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def measureLeft(self):
        self.data.gcode_queue.put("B10 L")
    
    def readMotorSpacing(self, dist):
        dist = dist - 2*6.35                                #subtract off the extra two links

        print "Read motor spacing: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorSpacingX', str(dist))
        
        #put some slack in the chain
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L10 ")
        self.data.gcode_queue.put("G90 ")
        
        self.readyToMoveOn()
    
    def pullChainTightAndMeasure(self):
        #pull the left chain tight
        self.data.gcode_queue.put("B11 S255 T3 L ")
        #request a measurement
        self.data.gcode_queue.put("B10 L")
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
        self.data.measureRequest = self.readMotorSpacing
        
        self.originalChainOverSproketDir = App.get_running_app().data.config.get('Advanced Settings', 'chainOverSprocket')
        
        #pretend we are in the "Top" configuration during this step
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', 'Top')
        
        #set the threshold for warning that the machine is off target to 200mm essentially turning it off. We don't want this to trigger when pulling the chain tight
        self.data.gcode_queue.put("$42=2000 ")
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        
        
        #Restore original chain over sprocket direction
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', self.originalChainOverSproketDir)
        #restore all settings to the values stored in the current settings file 
        self.data.gcode_queue.put("$$ ")
        
