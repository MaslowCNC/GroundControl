'''

A template for creating a new calibration step widget

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class QuadTestCut(GridLayout):
    readyToMoveOn               = ObjectProperty(None)
    numberOfTimesTestCutRun     = -2
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
    
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
    
    def switchUnits(self):
        if self.unitsBtn.text == 'MM':
            self.unitsBtn.text = 'Inches'
        else:
            self.unitsBtn.text = 'MM'
    
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
            self.on_Exit()
        else:
            amtToChange = .9*dif
            newSledSpacing = float(self.data.config.get('Maslow Settings', 'sledWidth')) + amtToChange
            print "Now trying spacing: " + str(newSledSpacing)
            self.data.config.set('Maslow Settings', 'sledWidth', str(newSledSpacing))
            self.cutBtn.disabled = False
    
    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        self.readyToMoveOn()