from   kivy.uix.widget                    import   Widget
from   kivy.properties                    import   ObjectProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
from UIElements.zAxisPopupContent              import ZAxisPopupContent

class AdjustZCalibrationDepth(Widget):
    '''
    
    Provides a standard interface for running the calibration test pattern for triangular kinematics 
    
    '''
    data                         =  ObjectProperty(None) #linked externally
    zStepSizeVal                 =  .1                   #The default movement size for the z-axis
    
    def on_enter(self):
        '''
        
        Called when the calibration process gets to this step
        
        '''
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
        self.data.config.write()
        self.data.pushSettings()
        
        #enable and disable the button to open the z-axis popup
        if self.zAxisActiveSwitch.active == True:
            self.openZPopupBtn.disabled        = False
        else:
            self.openZPopupBtn.disabled        = True
    
    def zAxisPopup(self):
        self.popupContent      = ZAxisPopupContent(done=self.dismissZAxisPopup)
        self.popupContent.data = self.data
        self.popupContent.initialize(self.zStepSizeVal)
        self._zpopup = Popup(title="Z-Axis", content=self.popupContent,
                            size_hint=(0.5, 0.5))
        self._zpopup.open()
    
    def dismissZAxisPopup(self):
        '''
        
        Close The Z-Axis Pop-up
        
        '''
        try:
            self.zStepSizeVal = float(self.popupContent.distBtn.text)
        except:
            pass
        self._zpopup.dismiss()
    
    def zeroZ(self):
        '''

        Define the z-axis to be currently at height 0

        '''
        self.data.gcode_queue.put("G10 Z0 ")
        self.carousel.load_next()