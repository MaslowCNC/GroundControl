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
            pass
        if self.carousel.index == 2:
            #measuring distance between motors
            self.data.measureRequest = self.readMotorSpacing
        if self.carousel.index == 3:
            #measure sled spacing
            pass
        if self.carousel.index == 4:
            #measure vertical distance to wood
            self.data.measureRequest = self.readVerticalOffset
        if self.carousel.index == 4:
            #review calculations
            self.reviewNumbers.text = "Let's review the measurements we've made so far to make sure they look correct\n\nMotor Spacing: " + str(self.data.config.get('Maslow Settings', 'motorSpacingX')) + "mm\nSled Mount Spacing: " + str(self.data.config.get('Maslow Settings', 'sledWidth')) + "mm\nVertical Offset: " + str(self.data.config.get('Maslow Settings', 'motorOffsetY')) + "mm\n\nYou can go back and re-do any of these numbers if you would like"
    
    def LeftCW(self):
        print "left CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
        self.data.gcode_queue.put("B09 L.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def LeftCCW(self):
        print "left CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
        self.data.gcode_queue.put("B09 L-.5 ")
        self.data.gcode_queue.put("G90 ")
        
    def RightCW(self):
        print "right CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
        self.data.gcode_queue.put("B09 R-.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def RightCCW(self):
        print "right CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
        self.data.gcode_queue.put("B09 R.5 ")
        self.data.gcode_queue.put("G90 ")
    
    def extendLeft(self, dist):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
        self.data.gcode_queue.put("B09 L" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def retractLeft(self, dist):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B06 L0 R0 ")
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
    
    def readVerticalOffset(self, dist):
        print "vertical offset measured at: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorOffsetY', str(dist))
        self.data.config.write()
        self.carousel.load_next()
    
    def countLinks(self):
        print "counting links, dist: "
        
        dist =  float(self.linksTextInput.text)*6.35
        
        print dist
        
        self.data.config.set('Maslow Settings', 'sledWidth', str(dist))
        self.data.config.write()
        self.carousel.load_next()
    
    def calibrateChainLengths(self):
        print "calibrating"
        self.data.gcode_queue.put("B02 ")
        
    def enterTestPaternValues(self):
        print "values entered"
        
    def cutTestPatern(self):
        print "would cut test pattern"
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90 ")
        self.data.gcode_queue.put("G0 X0 Y0 ")
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("G1 X50 Y50 F1000")
        self.data.gcode_queue.put("G1 X-50 ")
        self.data.gcode_queue.put("G1 Y-50 ")
        self.data.gcode_queue.put("G90 ")
    
    def stopCut(self):
        print "would stop cut"
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        