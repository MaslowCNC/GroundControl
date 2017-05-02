'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   UIElements.touchNumberInput               import   TouchNumberInput
from   kivy.uix.popup                            import   Popup

class MeasureMachinePopup(GridLayout):
    done   = ObjectProperty(None)
    
    def slideJustChanged(self):
        if self.carousel.index == 1:
            #pointing one sprocket up
            #self.data.gcode_queue.put("B06 L1900.1 R1900.1 ")
            pass
            
        if self.carousel.index == 2:
            #measuring distance between motors
            self.data.measureRequest = self.readMotorSpacing
    
    def LeftCW(self):
        print "left CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def LeftCCW(self):
        print "left CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-.5 ")
        self.data.gcode_queue.put("G90 ")
        
    def RightCW(self):
        print "right CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R-.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def RightCCW(self):
        print "right CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def extendLeft(self, dist):
        print "Extend left by " + str(dist) + "mm"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def retractLeft(self, dist):
        print "Retract left by " + str(dist) + "mm"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def setZero(self):
        #mark that the sprockets are straight up
        self.data.gcode_queue.put("B06 L0 R0 ");
        self.carousel.load_next()
    
    def measureLeft(self):
        self.data.gcode_queue.put("B10 L")
    
    def readMotorSpacing(self, dist):
        print "Read motor spacing: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorSpacingX', str(dist))
        self.data.config.write()
        self.carousel.load_next()
    
    def countLinks(self):
        print "counting links, dist: "
        
        dist =  float(self.linksTextInput.text)*6.35
        
        print dist
        
        self.data.config.set('Maslow Settings', 'sledWidth', str(dist))
        self.data.config.write()
        self.carousel.load_next()