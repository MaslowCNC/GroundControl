'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   UIElements.touchNumberInput               import   TouchNumberInput
from   kivy.uix.popup                            import   Popup

class ZAxisPopupContent(GridLayout):
    done   = ObjectProperty(None)
    zCutLabel = StringProperty("to...")
    zPopDisable = ObjectProperty(True)
    
    def initialize(self, zStepSizeVal):
        '''
        
        Initialize the z-axis popup
        
        '''
        self.unitsBtn.text = self.data.units
        self.distBtn.text  = str(zStepSizeVal)
        if self.data.zPush is not None:
            self.zCutLabel = "to:"+'%.2f'%(self.data.zPush)
            self.zPopDisable = self.data.zPushUnits <> self.data.units
    
    def setDist(self):
        self.popupContent = TouchNumberInput(done=self.dismiss_popup, data = self.data)
        self._popup = Popup(title="Change increment size of machine movement", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    
    def units(self):
        '''
        
        Toggle the machine units.
        
        '''
        if self.data.units == "INCHES":
            self.data.units = "MM"
            self.distBtn.text = "{0:.2f}".format(25.4*float(self.distBtn.text))
        else:
            self.data.units = "INCHES"
            
            self.distBtn.text = "{0:.2f}".format(float(self.distBtn.text)/25.4)
        
        self.unitsBtn.text = self.data.units
        
        if self.data.zPush is not None:
            self.zPopDisable = self.data.zPushUnits <> self.data.units
    
    def goThere(self):
        '''
        Go to the position (into work -- you can pop out to a safe height)
        '''
        self.data.gcode_queue.put("G00 Z"+ str(-1*float(self.distBtn.text)))
        
    
    def zIn(self):
        '''
        
        Move the z-axis in
        
        '''
        self.data.gcode_queue.put("G91 G00 Z" + str(-1*float(self.distBtn.text)) + " G90 ")
    
    def zOut(self):
        '''
        
        Move the z-axis out
        
        '''
        self.data.gcode_queue.put("G91 G00 Z" + str(self.distBtn.text) + " G90 ")
        
    def zUp(self):
        '''
        Move z-axis to safety
        '''
        #Save the current "cut" point
        self.data.zPush = self.data.zReadoutPos
        self.data.zPushUnits = self.units
        self.zCutLabel = "to:"+'%.2f'%(self.data.zPush)
        self.zPopDisable = False
        
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G00 Z.25 ")
        else:
            self.data.gcode_queue.put("G00 Z5.0 ")

    def zToZero(self):
        '''
        Move z-axis to zero
        '''
        self.data.gcode_queue.put("G00 Z0")
        
    def zToCut(self):
        '''
        Move z-axis to last cut (saved point when "move to safety" was pressed
        '''
        print "zspot", self.data.zPush
        self.data.gcode_queue.put("G00 Z"+str(self.data.zPush))
    
    def zero(self):
        '''
        
        Define the z-axis to be currently at height 0
        
        '''
        self.data.gcode_queue.put("G10 Z0 ")
        
    def touchZero(self):
        '''
        Probe for Zero Z
        '''
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G38.2 Z2 F2")    #Only go down 2 inches...
        else:
            self.data.gcode_queue.put("G38.2 Z50 F50")  #Or 50mm.
            
    
    def stopZMove(self):
        '''
        
        Send the immediate stop command
        
        '''
        print("z-axis Stopped")
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up to enter distance information
        
        '''
        try:
            tempfloat = float(self.popupContent.textInput.text)
            self.distBtn.text = str(tempfloat)  # Update displayed text using standard numeric format
        except:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()
