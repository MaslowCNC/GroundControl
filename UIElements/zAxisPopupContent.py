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
    zCutLabel = StringProperty("Re-Plunge To\nSaved Depth")
    zPopDisable = ObjectProperty(True)
    unitsArmed=False
    onEntryUnits=""
    
    def initialize(self):
        '''
        
        Initialize the z-axis popup
        
        '''
        self.onEntryUnits= self.data.units
        if self.data.zPopupUnits is None:
            self.data.zPopupUnits = self.data.units
        self.unitsBtn.text = self.data.zPopupUnits
        if self.data.zPush is not None:
            self.zCutLabel = "Re-Plunge to\n"+'%.3f '%(self.data.zPush)+self.data.zPushUnits[:2]
            self.zPopDisable=False
            
    def setMachineUnits(self, units=None):
        if units is None:
            units = self.data.zPopupUnits
            
        self.data.units = units #Show the right units on the main screen
        if units == "INCHES":
            self.data.gcode_queue.put('G20 ')
        else:
            self.data.gcode_queue.put('G21 ')

    def resetMachineUnits(self):
        self.data.units = self.onEntryUnits #Return main screen to old units
        if self.data.units == "INCHES":
            self.data.gcode_queue.put('G20 ')
        else:
            self.data.gcode_queue.put('G21 ')

    def setDist(self):
        self.popupContent = TouchNumberInput(done=self.dismiss_popup, data = self.data)
        self._popup = Popup(title="Change increment size of machine movement", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    
    def units(self):
        '''
        Toggle the dialog units.
        '''
        if self.data.zPopupUnits == "INCHES":
            self.data.zPopupUnits = "MM"
            self.data.zStepSizeVal=25.4*float(self.distBtn.text)
        else:
            self.data.zPopupUnits = "INCHES"
            self.data.zStepSizeVal=float(self.distBtn.text)/25.4
        
        self.distBtn.text = "%.3f"%self.data.zStepSizeVal
        self.unitsBtn.text = self.data.zPopupUnits
    
    def goThere(self):
        '''
        Go to the position (into work -- you can pop out to a safe height)
        '''
        self.setMachineUnits()
        self.data.gcode_queue.put("G00 Z"+ str(-1*float(self.distBtn.text)))
        self.resetMachineUnits()
        
    
    def zIn(self):
        '''
        Move the z-axis in
        '''
        self.setMachineUnits()
        self.data.gcode_queue.put("G91 G00 Z" + str(-1*float(self.distBtn.text)) + " G90 ")
        self.resetMachineUnits()

    def zOut(self):
        '''        
        Move the z-axis out
        '''
        self.setMachineUnits()
        self.data.gcode_queue.put("G91 G00 Z" + str(self.distBtn.text) + " G90 ")
        self.resetMachineUnits()
        
    def zUp(self):
        '''
        Move z-axis to safety
        '''
        #Save the current "cut" point
        self.data.zPush = self.data.zReadoutPos
        self.data.zPushUnits = self.data.units
        self.zCutLabel = "Re-Plunge to\n"+'%.3f '%(self.data.zPush)+self.data.zPushUnits[:2]
        self.zPopDisable = False
        
        self.setMachineUnits()
        safeHeightMM = float(self.data.config.get('Maslow Settings', 'zAxisSafeHeight'))
        safeHeightInches = safeHeightMM / 25.5
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
        else:
            self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
        self.resetMachineUnits()

    def zToZero(self):
        '''
        Move z-axis to zero
        '''
        self.data.gcode_queue.put("G00 Z0") #Zero is zero in mm or in ;)
        
    def zToCut(self):
        '''
        Move z-axis to last cut (saved point when "move to safety" was pressed
        '''
        self.setMachineUnits(self.data.zPushUnits)
        self.data.gcode_queue.put("G00 Z"+str(self.data.zPush))
        self.resetMachineUnits()
    
    def zero(self):
        '''
        
        Define the z-axis to be currently at height 0
        
        '''
        self.data.gcode_queue.put("G10 Z0 ")
        
    def touchZero(self):
        '''
        Probe for Zero Z
        '''
        self.setMachineUnits()
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G38.2 Z-.2 F2")    #Only go down 0.2 inches...
        else:
            self.data.gcode_queue.put("G38.2 Z-5 F50")  #Or 5mm.
        self.resetMachineUnits()
            
    
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
            self.data.zStepSizeVal=tempfloat  # Update displayed text using standard numeric format
            self.distBtn.text = "%.3f"%tempfloat
        except ValueError:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()
        
    def close(self):
        self.done()
