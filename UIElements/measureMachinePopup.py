'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   UIElements.touchNumberInput               import   TouchNumberInput
from   UIElements.triangularCalibration          import   TriangularCalibration
from   UIElements.adjustZCalibrationDepth        import   AdjustZCalibrationDepth
from   kivy.uix.popup                            import   Popup
import global_variables

class MeasureMachinePopup(GridLayout):
    done                         = ObjectProperty(None)
    stepText                     = StringProperty("Step 1 of 10")
    numberOfTimesTestCutRun      = -2
    kinematicsType               = 'Quadrilateral'

    def establishDataConnection(self, data):
        '''

        Sets up the data connection between this popup and the shared data object

        '''

        self.data = data

        self.setSprocketsVertical.data      =  data
        self.setSprocketsVertical.carousel  =  self.carousel

        self.measureOutChains.data          =  data
        self.measureOutChains.carousel      =  self.carousel
        self.measureOutChains.text          =  "Now we are going to measure out the chains and reattach the sled\n\nHook the first link of the right chain on the vertical tooth of the right sprocket\n as shown in the picture below\n\nThe left chain does not need to be moved, it can be left partly extended\n\nThe correct length of first the left and then the right chain will be measured out\n\nOnce both chains are finished attach the sled, then press Next\nPressing Next will move the sled to the center of the sheet.\n\nBe sure to keep an eye on the chains during this process to ensure that they do not become tangled\naround the sprocket. The motors are very powerful and the machine can damage itself this way"
        
        self.adjustZStep.data               =  data
        self.adjustZStep.carousel           =  self.carousel
        
        self.triangularCalibration.data          =  data
        self.triangularCalibration.carousel      =  self.carousel
        triangularTestCutText = "The cuts in the corners will be about\n254 mm/10 inches from the work area edges.\n\n"
        triangularTestCutText = triangularTestCutText + "The pattern will be centered in the work area with dimensions:\n"
        triangularTestCutText = triangularTestCutText + "Width: " + str(float(self.data.config.get('Maslow Settings', 'bedWidth'))-508) + " mm/" + str((float(self.data.config.get('Maslow Settings', 'bedWidth'))-508)/25.4) + " inches\n"
        triangularTestCutText = triangularTestCutText + "Height: " + str(float(self.data.config.get('Maslow Settings', 'bedHeight'))-508) + " mm/" + str((float(self.data.config.get('Maslow Settings', 'bedHeight'))-508)/25.4) + " inches\n"
        self.triangularCalibration.triangularCalText  = triangularTestCutText

    def backBtn(self, *args):
        '''

        Runs when the back button is pressed

        '''

        if self.carousel.index == 10 and self.kinematicsType == 'Quadrilateral':                                        #if we're at the test cut for quadrilateral and we want to go back to choosing kinematics type
            self.carousel.load_slide(self.carousel.slides[8])
        elif self.carousel.index == 11 and self.kinematicsType == 'Triangular':                                      #if we're at the last step and need to go back but but we want to go back to the triangular kinematics test cut
            self.carousel.load_slide(self.carousel.slides[9])
        else:
            self.carousel.load_previous()

    def fwdBtn(self, *args):
        '''

        Runs when the skip button is pressed

        '''

        if self.carousel.index == 8 and self.kinematicsType == 'Quadrilateral':                                         #If the kinematics type is quadrilateral skip to the quadrilateral test
            self.carousel.load_slide(self.carousel.slides[10])
        elif self.carousel.index == 9 and self.kinematicsType == 'Triangular':                                       #If we're in the cut test shape triangular and we want to skip to the end
            self.carousel.load_slide(self.carousel.slides[11])
        else:
            self.carousel.load_next()

    def slideJustChanged(self):
        '''
        
        Runs when the slide has just been changed
        
        '''
        
        print self.carousel.slides
        #self.carousel.slides[self.carousel.index].on_enter()
        
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
            self.adjustZStep.on_enter()
            self.stepText = "Step 8 of 10"

        if self.carousel.index == 8:
            #Choose kinematics type
            self.stepText = "Step 9 of 10"

        if self.carousel.index == 9:
            #Cut test shape triangular
            self.data.pushSettings()
            self.stepText = "Step 10 of 10"
            self.goFwdBtn.disabled = False

            #if we're not supposed to be in triangular calibration go to the next page
            if self.kinematicsType != 'Triangular':
                self.carousel.load_next()

        if self.carousel.index == 10:
            #Cut test shape quadrilateral
            self.data.pushSettings()
            self.goFwdBtn.disabled = False
            self.stepText = "Step 10 of 10"

            #if we're not supposed to be in quadratic calibration go to finished
            if self.kinematicsType == 'Triangular':
                self.carousel.load_next()

        if self.carousel.index == 11:
            #Final finish step
            self.goFwdBtn.disabled = True
            finishString = "Your machine is now calibrated!\n\nCongratulations!\n\nThe final calibration values are:\n"
            finishString = finishString + "\nDistance between motors: " + self.data.config.get('Maslow Settings', 'motorSpacingX') + "mm"
            finishString = finishString + "\nVertical motor offset: " + self.data.config.get('Maslow Settings', 'motorOffsetY') + "mm"
            finishString = finishString + "\nKinematics type: " + self.data.config.get('Advanced Settings', 'kinematicsType')
            if self.data.config.get('Advanced Settings', 'kinematicsType') == 'Triangular':
                finishString = finishString + "\nRotation radius: " + self.data.config.get('Advanced Settings', 'rotationRadius') + "mm"
                finishString = finishString + "\nChain sag correction value: " + self.data.config.get('Advanced Settings', 'chainSagCorrection')
            else:
                finishString = finishString + "\nSled mount spacing: " + self.data.config.get('Maslow Settings', 'sledWidth') + "mm"

            self.finishText.text = finishString

    def begin(self):

        self.carousel.load_next()

    def defineInitialState(self):
        '''

        This is a place to do any preparation needed on beginning the automatic calibration process. If putting something here, consider how it would
        affect a user that uses 'Begin' but does not complete the process. Should the preparation be reversable to allow a clean bailout?

        '''
        self.carousel.load_next()
            
    def extendLeft(self, dist):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")

    def retractLeft(self, dist):
        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L-" + str(dist) + " ")
        self.data.gcode_queue.put("G90 ")

    def measureLeft(self):
        self.data.gcode_queue.put("B10 L")

    def readMotorSpacing(self, dist):

        dist = dist - 2*6.35                                #subtract off the extra two links

        print "Read motor spacing: " + str(dist)
        self.data.config.set('Maslow Settings', 'motorSpacingX', str(dist))
        self.data.config.write()

        self.extendLeft(15);

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

    def textInputPopup(self, target):
        self.targetWidget = target

        self.popupContent = TouchNumberInput(done=self.dismiss_popup, data = self.data)
        self._popup = Popup(title="Number of links", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        if global_variables._keyboard:
            global_variables._keyboard.bind(on_key_down=self.keydown_popup)
            self._popup.bind(on_dismiss=self.ondismiss_popup)

    def dismiss_popup(self):
        try:
            tempfloat = float(self.popupContent.textInput.text)
            self.targetWidget.text = str(tempfloat)  # Update displayed text using standard numeric format
        except:
            pass  # If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()

    def ondismiss_popup(self, event):
       if global_variables._keyboard:
           global_variables._keyboard.unbind(on_key_down=self.keydown_popup)

    def keydown_popup(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == '0') or (keycode[1] =='numpad0'):
            self.popupContent.addText('0')
        elif (keycode[1] == '1') or (keycode[1] =='numpad1'):
            self.popupContent.addText('1')
        elif (keycode[1] == '2') or (keycode[1] =='numpad2'):
            self.popupContent.addText('2')
        elif (keycode[1] == '3') or (keycode[1] =='numpad3'):
            self.popupContent.addText('3')
        elif (keycode[1] == '4') or (keycode[1] =='numpad4'):
            self.popupContent.addText('4')
        elif (keycode[1] == '5') or (keycode[1] =='numpad5'):
            self.popupContent.addText('5')
        elif (keycode[1] == '6') or (keycode[1] =='numpad6'):
            self.popupContent.addText('6')
        elif (keycode[1] == '7') or (keycode[1] =='numpad7'):
            self.popupContent.addText('7')
        elif (keycode[1] == '8') or (keycode[1] =='numpad8'):
            self.popupContent.addText('8')
        elif (keycode[1] == '9') or (keycode[1] =='numpad9'):
            self.popupContent.addText('9')
        elif (keycode[1] == '.') or (keycode[1] =='numpaddecimal'):
            self.popupContent.addText('.')
        elif (keycode[1] == 'backspace'):
            self.popupContent.textInput.text = self.popupContent.textInput.text[:-1]
        elif (keycode[1] == 'enter') or (keycode[1] =='numpadenter'):
            self.popupContent.done()
        elif (keycode[1] == 'escape'):     # abort entering a number, keep the old number
            self.popupContent.textInput.text = ''    # clear text so it isn't converted to a number
            self.popupContent.done()
        return True     # always swallow keypresses since this is a modal dialog

    def countLinks(self):
        print "counting links, dist: "

        try:
            dist =  float(self.linksTextInput.text)*6.35
        except:
            self.carousel.load_next()
            return

        self.data.config.set('Maslow Settings', 'sledWidth', str(dist))
        self.data.config.write()

        self.carousel.load_next()

    def calibrateChainLengths(self):
        print "calibrating"
        self.data.gcode_queue.put("B02 ")

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

    def setKinematicsType(self, kinematicsType, *args):
        '''

        Update kinematics to the value shown in the drop down and move to the next step

        '''
        self.kinematicsType = kinematicsType

        print "Kinematics set to: "
        print self.kinematicsType

        self.data.config.set('Advanced Settings', 'kinematicsType', self.kinematicsType)
        self.data.config.write()

        if self.kinematicsType == 'Triangular':
            try:
                #Get the value if it's already there...
                 rotationRadius = self.data.config.get('Advanced Settings', 'rotationRadius')
                 print "Current rotation radius is " + str(rotationRadius)
            except:
                #Set up a good initial guess for the radius
                print "Rotation radius set to 260"
                self.data.config.set('Advanced Settings', 'rotationRadius', 260)
                self.data.config.write()
            self.carousel.load_next()
        else:

            self.carousel.load_slide(self.carousel.slides[10])

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

    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()

    def switchUnits(self):
        if self.unitsBtn.text == 'MM':
            self.unitsBtn.text = 'Inches'
        else:
            self.unitsBtn.text = 'MM'

    