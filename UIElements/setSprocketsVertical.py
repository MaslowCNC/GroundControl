from kivy.uix.widget                      import   Widget
from kivy.properties                      import   ObjectProperty

class SetSprocketsVertical(Widget):
    '''
    
    Provides a standard interface for making both sprockets point vertically
    
    '''
    data = ObjectProperty(None) #set externally
    
    def LeftCW(self):
        
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def LeftCCW(self):
        
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-.5 ")
        self.data.gcode_queue.put("G90 ")
        
    def RightCW(self):
        #print "right CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R-.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def RightCCW(self):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def setZero(self):
        #mark that the sprockets are straight up
        self.data.gcode_queue.put("B06 L0 R0 ");
        self.carousel.load_next()