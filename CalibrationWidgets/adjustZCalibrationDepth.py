from   kivy.uix.gridlayout                      import   GridLayout
from   kivy.properties                          import   ObjectProperty
from   UIElements.touchNumberInput              import   TouchNumberInput
from   kivy.uix.popup                           import   Popup
from UIElements.zAxisPopupContent               import ZAxisPopupContent
from   kivy.app                                 import   App

class AdjustZCalibrationDepth(GridLayout):
    '''
    
    Provides a standard interface for setting up the Z axis 
    
    '''
    data                         =  ObjectProperty(None) #linked externally
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
        
        if int(self.data.config.get('Maslow Settings', 'zAxis')) == 1:
            self.zAxisActiveSwitch.active = True
            self.openZPopupBtn.disabled        = False
        else:
            self.zAxisActiveSwitch.active = False
            self.openZPopupBtn.disabled        = True
    
    def enableZaxis(self, *args):
        '''

        Triggered when the switch to enable the z-axis is touched

        '''
        self.data.config.set('Maslow Settings', 'zAxis', int(self.zAxisActiveSwitch.active))
        
        #enable and disable the button to open the z-axis popup
        if self.zAxisActiveSwitch.active == True:
            self.openZPopupBtn.disabled        = False
        else:
            self.openZPopupBtn.disabled        = True
    
    def zAxisPopup(self):
        self.popupContent      = ZAxisPopupContent(done=self.dismissZAxisPopup)
        self.popupContent.data = self.data
        self.popupContent.initialize()
        self._zpopup = Popup(title="Z-Axis", content=self.popupContent,
                            size_hint=(0.5, 0.5))
        self._zpopup.open()
    
    def dismissZAxisPopup(self):
        '''
        
        Close The Z-Axis Pop-up
        
        '''
        self._zpopup.dismiss()
    
    def zeroZ(self):
        '''

        Define the z-axis to be currently at height 0 and move to the next step.

        '''
        self.data.gcode_queue.put("G10 Z0 ")        #Set z-zero
        if self.data.units == "INCHES":             #Go to traverse
            self.data.gcode_queue.put("G00 Z.25 ")
        else:
            self.data.gcode_queue.put("G00 Z5.0 ") #these should use safe retract settings
        
        self.on_Exit()
    
    def on_Exit(self):
        '''
        
        This function runs when the step is completed
        
        '''
        
        self.readyToMoveOn()