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
    numberOfTimesTestCutRun = -2
    
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
            self.updateReviewValuesText()
        if self.carousel.index == 7:
            if int(self.data.config.get('Maslow Settings', 'zAxis')) == 1:
                self.zAxisActiveSwitch.active = True
            else:
                self.zAxisActiveSwitch.active = False
        if self.carousel.index == 8:
            #Cut test shape
            self.goFwdBtn.disabled = False
            self.data.pushSettings()
        if self.carousel.index == 10:
            #Final finish step
            self.goFwdBtn.disabled = True
    
	def begin(self):
		print "begin fcn ran"
		self.carousel.load_next()
    
    def defineInitialState(self):
        '''
        
        Ensure that the calibration process begins with known initial conditions for where the axis
        think that they are are by setting both to zero. This prevents strange behavior when rotating
        each sprocket to 12:00
        
        '''
        print "define initial state"
        self.data.gcode_queue.put("B06 L0 R0 ");
        self.carousel.load_next()
    
    def LeftCW(self):
        print "left CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L.5 F100 ")
        self.data.gcode_queue.put("G90 ")
    
    def LeftCCW(self):
        print "left CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-.5 F100 ")
        self.data.gcode_queue.put("G90 ")
        
    def RightCW(self):
        print "right CW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R-.5 F100 ")
        self.data.gcode_queue.put("G90 ")
    
    def RightCCW(self):
        print "right CCW"
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 R.5 F100 ")
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
        
        dist = dist - 2*6.35                                #subtract off the extra two links
        
        print "Read motor spacing: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorSpacingX', str(dist))
        self.data.config.write()
        self.carousel.load_next()
    
    def readVerticalOffset(self, dist):
        print "vertical offset measured at: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorOffsetY', str(dist))
        self.data.config.write()
        
        
        #keep updating the values shown because sometimes it takes a while for the settings to write
        from kivy.clock import Clock
        Clock.schedule_once(self.updateReviewValuesText, .1)
        Clock.schedule_once(self.updateReviewValuesText, .2)
        Clock.schedule_once(self.updateReviewValuesText, .3)
        Clock.schedule_once(self.updateReviewValuesText, .4)
        
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
    
    def enableZaxis(self, *args):
        '''
        
        Triggered when the switch to enable the z-axis is touched
        
        '''
        self.data.config.set('Maslow Settings', 'zAxis', int(self.zAxisActiveSwitch.active))
        self.data.config.write()
    
    def pullChainTight(self):
        #pull the left chain tight
        self.data.gcode_queue.put("B11 S50 T3 ")
    
    def updateReviewValuesText(self, *args):
        '''
        
        Update the text which displays the measured values
        
        '''
        self.reviewNumbers.text = "Let's review the measurements we've made so far to make sure they look correct\n\nMotor Spacing: " + str(self.data.config.get('Maslow Settings', 'motorSpacingX')) + "mm\nSled Mount Spacing: " + str(self.data.config.get('Maslow Settings', 'sledWidth')) + "mm\nVertical Offset: " + str(self.data.config.get('Maslow Settings', 'motorOffsetY')) + "mm\n\nYou can go back and re-do any of these numbers if you would like"
        print "updating text"
    
    def setKinematicsType(self, *args):
        '''
        
        Update kinematics to the value shown in the drop down and move to the next step
        
        '''
        print "Kinematics set to: "
        print self.chooseKinematicsType.text
        
        self.data.config.set('Maslow Settings', 'kinematicsType', self.chooseKinematicsType.text)
        self.data.config.write()
        
        self.carousel.load_next()
    
    def cutTestPaternTriangular(self):
        
        #Credit for this test pattern to DavidLang
        self.data.units = "MM"
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G40 ")

        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G17 ")

        #(defines the center)
        self.data.gcode_queue.put("G0 X" + str(18*self.numberOfTimesTestCutRun) + " Y" + str(-18*self.numberOfTimesTestCutRun) + "  ")
        self.data.gcode_queue.put("G91 ")

        self.data.gcode_queue.put("G0 X-902.5 ")
        self.data.gcode_queue.put("G1 Z-7 F500 ")
        self.data.gcode_queue.put("G1 Y-20 ")
        self.data.gcode_queue.put("G1 Z7 ")
        self.data.gcode_queue.put("G0 X1905 Y20 ")
        self.data.gcode_queue.put("G1 Z-7 ")
        self.data.gcode_queue.put("G1 Y-20 ")
        self.data.gcode_queue.put("G1 Z5 ")
        
        
        self.data.gcode_queue.put("G90  ")
        
        self.numberOfTimesTestCutRun = self.numberOfTimesTestCutRun + 1
        self.cutBtn.text = "Re-Cut Test\nPattern"
        self.cutBtn.disabled         = True
        self.horizMeasure.disabled   = False
        self.vertMeasure.disabled    = False
        self.unitsBtn.disabled       = False
        self.enterValues.disabled    = False
    
    def cutTestPatern(self):
        
        #Credit for this test pattern to DavidLang
        self.data.units = "MM"
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
        self.data.gcode_queue.put("G90  ")
        
        self.numberOfTimesTestCutRun = self.numberOfTimesTestCutRun + 1
        self.cutBtn.text = "Re-Cut Test\nPattern"
        self.cutBtn.disabled         = True
        self.horizMeasure.disabled   = False
        self.vertMeasure.disabled    = False
        self.unitsBtn.disabled       = False
        self.enterValues.disabled    = False
    
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
            amtToChange = .9*dif
            newSledSpacing = float(self.data.config.get('Maslow Settings', 'sledWidth')) + amtToChange
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Maslow Settings', 'sledWidth', str(newSledSpacing))
            self.data.config.write()
            self.cutBtn.disabled = False
            self.data.pushSettings()
    
    def enterTestPaternValuesTriangular(self):
        
        dist = 0
        
        try:
            dist = float(self.TriangularMeasure.text)
        except:
            self.data.message_queue.put("Message: Couldn't make that into a number")
            return
        
        if self.unitsBtn.text == 'Inches':
            print "inches seen"
            dist = dist*25.4
        
        acceptableTolerance = .5
        
        if abs(dist) < acceptableTolerance:               #if we're fully calibrated
            self.carousel.load_next()
        else:
            amtToChange = .9*dist
            newSledSpacing = float(self.data.config.get('Maslow Settings', 'sledWidth')) + amtToChange
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Maslow Settings', 'sledWidth', str(newSledSpacing))
            self.data.config.write()
            self.cutBtn.disabled = False
            self.data.pushSettings()
    
    def stopCut(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def switchUnits(self):
        if self.unitsBtn.text == 'MM':
            self.unitsBtn.text = 'Inches'
        else:
            self.unitsBtn.text = 'MM'
    
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