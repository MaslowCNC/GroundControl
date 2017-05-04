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
    numberOfTimesTestCutRun = 0
    
    def slideJustChanged(self):
        if self.carousel.index == 0:
            #begin notes
            self.goBackBtn.disabled = True
        if self.carousel.index == 1:
            #pointing one sprocket up
            self.goBackBtn.disabled = False
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
        if self.carousel.index == 7:
            #Final finish step
            self.goFwdBtn.disabled = False
        if self.carousel.index == 8:
            #Final finish step
            self.goFwdBtn.disabled = True
        
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
        self.data.gcode_queue.put("B09 L" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")
    
    def retractLeft(self, dist):
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
        from kivy.clock import Clock
        Clock.schedule_once(self.carousel.load_next, .1)            #give the settings a chance to finish writing
    
    def calibrateChainLengths(self):
        print "calibrating"
        self.data.gcode_queue.put("B02 ")
        
    def enterTestPaternValues(self):
        
        dif = 0
        
        try:
            dif = float(self.horizMeasure.text) - float(self.vertMeasure.text)
        except:
            self.data.message_queue.put("Message: Couldn't make that into a number")
            return
        
        if self.unitsBtn.text == 'Inches':
            print "inches seen"
            dif = dif*25.4
        
        acceptableTolerance = .5
        
        if abs(dif) < acceptableTolerance:               #if we're fully calibrated
            self.carousel.load_next()
        else:
            amtToChange = .5*dif
            newSledSpacing = float(self.data.config.get('Maslow Settings', 'sledWidth'))
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Maslow Settings', 'sledWidth', str(newSledSpacing))
            self.data.config.write()
            self.cutBtn.disabled = False
        
        
    def cutTestPatern(self):
        
        #Credit for this test pattern to DavidLang
        #self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G40 ")

        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G17 ")

        #(defines the center)
        self.data.gcode_queue.put("G0 X" + str(18*self.numberOfTimesTestCutRun) + " Y" + str(-18*self.numberOfTimesTestCutRun) + "  ")
        self.data.gcode_queue.put("G91 ")

        self.data.gcode_queue.put("G0 X-300 Y300  ")
        self.data.gcode_queue.put("G1 Z-7 F500  ")
        self.data.gcode_queue.put("G1 Y18  ")
        self.data.gcode_queue.put("G1 Z7  ")
        self.data.gcode_queue.put("G0 X600 Y-18 ")
        self.data.gcode_queue.put("G1 Z-7  ")
        self.data.gcode_queue.put("G1 Y18  ")
        self.data.gcode_queue.put("G1 X-18 ")
        self.data.gcode_queue.put("G1 Z7 ")
        self.data.gcode_queue.put("G0 X18 Y-600 ")
        self.data.gcode_queue.put("G1 Z-7  ")
        self.data.gcode_queue.put("G1 X-18  ")
        self.data.gcode_queue.put("G1 Z7  ")
        self.data.gcode_queue.put("G0 X-600 ")
        
        self.numberOfTimesTestCutRun = self.numberOfTimesTestCutRun + 1
        self.cutBtn.text = "Re-Cut Test\nPattern"
        self.cutBtn.disabled         = True
        self.horizMeasure.disabled   = False
        self.vertMeasure.disabled    = False
        self.unitsBtn.disabled       = False
        self.enterValues.disabled    = False
    
    def stopCut(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def switchUnits(self):
        if self.unitsBtn.text == 'MM':
            self.unitsBtn.text = 'Inches'
        else:
            self.unitsBtn.text = 'MM'
        