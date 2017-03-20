from kivy.uix.floatlayout                        import    FloatLayout
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs

class Diagnostics(FloatLayout, MakesmithInitFuncs):
    pass
    
    def returnToCenter(self):
        self.data.gcode_queue.put("G00 Z0 ")
        self.data.gcode_queue.put("G00 X0 Y0 Z0 ")
    
    def calibrateMotors(self):
        self.data.gcode_queue.put("B01")
        
    def calibrateChainLengths(self):
        self.data.gcode_queue.put("B02 ")
    
    def testMotors(self):
        self.data.gcode_queue.put("B04 ")
    
