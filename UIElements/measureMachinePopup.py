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
    stepText = StringProperty("Step 1 of 10")
    numberOfTimesTestCutRun = -2
    
    def slideJustChanged(self):
        
        if self.carousel.index == 0:
            #begin notes
            self.goBackBtn.disabled = True
            self.stepText = "Step 1 of 10"
        
        if self.carousel.index == 1:
            #pointing one sprocket up
            self.goBackBtn.disabled = False
            self.stepText = "Step 2 of 10"
        
        if self.carousel.index == 2:
            #measuring distance between motors
            self.data.measureRequest = self.readMotorSpacing
            self.stepText = "Step 3 of 10"
        
        if self.carousel.index == 3:
            #measure sled spacing
            self.stepText = "Step 4 of 10"
            pass
        
        if self.carousel.index == 4:
            #measure vertical distance to wood
            self.data.measureRequest = self.readVerticalOffset
            self.stepText = "Step 5 of 10"
        
        if self.carousel.index == 5:
            #review calculations
            self.updateReviewValuesText()
            self.stepText = "Step 6 of 10"
        
        if self.carousel.index == 6:
            #Calibrate chain lengths
            self.stepText = "Step 7 of 10"
        
        if self.carousel.index == 7:
            #set up z-axis
            if int(self.data.config.get('Maslow Settings', 'zAxis')) == 1:
                self.zAxisActiveSwitch.active = True
            else:
                self.zAxisActiveSwitch.active = False
            self.stepText = "Step 8 of 10"
        
        if self.carousel.index == 8:
            #Choose kinematics type
            self.stepText = "Step 9 of 10"
        
        if self.carousel.index == 9:
            #Cut test shape triangular
            self.data.pushSettings()
            self.stepText = "Step 10 of 10"
            
            #if we're not supposed to be in triangular calibration go to the next page
            if self.chooseKinematicsType.text != 'Triangular':
                self.carousel.load_next()
        
        if self.carousel.index == 10:
            #Cut test shape quadratic
            self.data.pushSettings()
            self.goFwdBtn.disabled = False
            self.stepText = "Step 10 of 10"
            
            #if we're not supposed to be in quadratic calibration go to finished
            if self.chooseKinematicsType.text == 'Triangular':
                self.carousel.load_next()
        
        if self.carousel.index == 11:
            #Final finish step
            self.goFwdBtn.disabled = True
    
    def begin(self):
        
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
        
        self.extendLeft(10);
        
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
    
    def finishChainCalibration(self, *args):
        #adjust chain lengths to put the sled in the center
        self.data.gcode_queue.put("B15 ")
        self.carousel.load_next()
    
    def setKinematicsType(self, *args):
        '''
        
        Update kinematics to the value shown in the drop down and move to the next step
        
        '''
        print "Kinematics set to: "
        print self.chooseKinematicsType.text
        
        self.data.config.set('Maslow Settings', 'kinematicsType', self.chooseKinematicsType.text)
        self.data.config.write()
        
        if self.chooseKinematicsType.text == 'Triangular':
            #Set up a good initial guess for the radius
            print "Rotation radius set to 260"
            self.data.config.set('Advanced Settings', 'rotationRadius', 260)
            self.data.config.write()
            self.carousel.load_next()
        else:
            
            self.carousel.load_slide(self.carousel.slides[10])
    
    def cutTestPaternTriangular(self):
        
        #Credit for this test pattern to David Lang
        self.data.units = "MM"
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90  ") #Switch to absolute mode
        self.data.gcode_queue.put("G40 ")

        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G17 ")

        #(defines the center). Moves up with each attempt
        self.data.gcode_queue.put("G0 X" +  str(18*self.numberOfTimesTestCutRun) + " Y" + str(-400 + 18*self.numberOfTimesTestCutRun) + "  ")
        
        self.data.gcode_queue.put("G91 ")   #Switch to relative mode

        self.data.gcode_queue.put("G0 X-902.5 ")
        self.data.gcode_queue.put("G1 Z-7 F500 ")
        self.data.gcode_queue.put("G1 Y-20 ")
        self.data.gcode_queue.put("G1 Z7 ")
        self.data.gcode_queue.put("G0 X1905 Y20 ")
        self.data.gcode_queue.put("G1 Z-7 ")
        self.data.gcode_queue.put("G1 Y-20 ")
        self.data.gcode_queue.put("G1 Z5 ")
        self.data.gcode_queue.put("G0 X-900 Y500 ")
        
        
        self.data.gcode_queue.put("G90  ") #Switch back to absolute mode
        
        self.numberOfTimesTestCutRun = self.numberOfTimesTestCutRun + 1
        self.cutBtnT.text = "Re-Cut Test\nPattern"
        self.cutBtnT.disabled         = True
        self.triangleMeasure.disabled = False
        self.unitsBtnT.disabled       = False
        self.enterValuesT.disabled    = False
    
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
        
        print "got to enter test values"
        
        dist = 0
        
        try:
            dist = float(self.triangleMeasure.text)
        except:
            self.data.message_queue.put("Message: Couldn't make that into a number")
            return
        
        if self.unitsBtn.text == 'Inches':
            dist = dist*25.4
        
        dist = 1905 - dist #1905 is expected test spacing in mm. dist is greater than zero if the length is too long, less than zero if if is too short
        
        print "The error is: "
        print dist
        
        acceptableTolerance = .5
        
        if abs(dist) < acceptableTolerance:               #if we're fully calibrated
            self.carousel.load_slide(self.carousel.slides[11])
        else:
            amtToChange = -.9*dist
            
            print "so we are going to adjust the motor spacing by: "
            print amtToChange
            
            newSledSpacing = float(self.data.config.get('Advanced Settings', 'rotationRadius')) + amtToChange
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Advanced Settings', 'rotationRadius', str(newSledSpacing))
            self.data.config.write()
            self.cutBtnT.disabled = False
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