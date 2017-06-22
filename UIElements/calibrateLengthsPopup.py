'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   kivy.uix.popup                            import   Popup

class CalibrateLengthsPopup(GridLayout):
    done   = ObjectProperty(None)
    
    def LeftCW(self):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def LeftCCW(self):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-.5 ")
        self.data.gcode_queue.put("G90 ")
        
    def RightCW(self):
        print "right CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R-.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def RightCCW(self):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def stop(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def setZero(self):
        #mark that the sprockets are straight up
        self.data.gcode_queue.put("B06 L0 R0 ");
        self.carousel.load_next()
    
    def calibrateChainLengths(self):
        self.data.gcode_queue.put("B02 ")
        
    