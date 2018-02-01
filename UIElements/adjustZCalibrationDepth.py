from   kivy.uix.widget                    import   Widget
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup

class AdjustZCalibrationDepth(Widget):
    '''
    
    Provides a standard interface for running the calibration test pattern for triangular kinematics 
    
    '''
    data                         =  ObjectProperty(None) #linked externally
    
    def on_enter(self):
        '''
        
        Called when the calibration process gets to this step
        
        '''
        if int(self.data.config.get('Maslow Settings', 'zAxis')) == 1:
            self.zAxisActiveSwitch.active = True
        else:
            self.zAxisActiveSwitch.active = False
    
    def moveZ(self, dist):
        '''

        Move the z-axis the specified distance

        '''
        self.data.units = "MM"
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G91 G00 Z" + str(dist) + " G90 ")

    def zeroZ(self):
        '''

        Define the z-axis to be currently at height 0

        '''
        self.data.gcode_queue.put("G10 Z0 ")
        self.carousel.load_next()
    
    def enableZaxis(self, *args):
        '''

        Triggered when the switch to enable the z-axis is touched

        '''
        self.data.config.set('Maslow Settings', 'zAxis', int(self.zAxisActiveSwitch.active))
        self.data.config.write()
        self.data.pushSettings()