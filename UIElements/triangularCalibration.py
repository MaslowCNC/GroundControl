from kivy.uix.widget                      import   Widget
from kivy.properties                      import   ObjectProperty

class TriangularCalibration(Widget):
    '''
    
    Provides a standard interface for running the calibration test pattern for triangular kinematics 
    
    '''
    data                         =  ObjectProperty(None) #linked externally
    numberOfTimesTestCutRun      = -2
    
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
        self.data.gcode_queue.put("G0 X0 Y" + str(self.testCutPosSlider.value) + "  ")
        
        self.testCutPosSlider.value = self.testCutPosSlider.value + 18 #increment the starting spot
        
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
        
        self.enterValuesT.disabled = False
    
    def enterTestPaternValuesTriangular(self):
        
        dist = 0
        
        try:
            dist = float(self.triangleMeasure.text)
        except:
            self.data.message_queue.put("Message: Couldn't make that into a number")
            return
        
        if self.unitsBtnT.text == 'Inches':
            dist = dist*25.4
        
        errorAmt = 1905 - dist #1905 is expected test spacing in mm. dist is greater than zero if the length is too long, less than zero if if is too short
        
        print "The error is: "
        print errorAmt
        
        acceptableTolerance = .5
        maximumRealisticError = 300
        
        if abs(errorAmt) > maximumRealisticError:
            self.data.message_queue.put('Message: ' + str(dist) + 'mm is ' + str(errorAmt) + 'mm away from the target distance of 1905mm which seems wrong.\nPlease check the number and enter it again.')
        elif abs(errorAmt) < acceptableTolerance:               #if we're fully calibrated
            self.carousel.load_slide(self.carousel.slides[11])
        else:
            amtToChange = -.9*errorAmt
            
            print "so we are going to adjust the motor spacing by: "
            print amtToChange
            
            newSledSpacing = float(self.data.config.get('Advanced Settings', 'rotationRadius')) + amtToChange
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Advanced Settings', 'rotationRadius', str(newSledSpacing))
            self.data.config.write()
            self.cutBtnT.disabled = False
            self.data.pushSettings()
            
            self.enterValuesT.disabled = True              #disable the button so the same number cannot be entered twice
    
    def stopCut(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        
        self.cutBtnT.disabled = False
    
    def switchUnits(self):
        if self.unitsBtnT.text == 'MM':
            self.unitsBtnT.text = 'Inches'
        else:
            self.unitsBtnT.text = 'MM'