'''

This allows the user interact with the z-axis when it is the content of a popup

'''
from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty

class ZAxisPopupContent(GridLayout):
    done   = ObjectProperty(None)
    
    def initialize(self):
        '''
        
        Initialize the z-axis popup
        
        '''
        self.unitsBtn.text = self.data.units
    
    def units(self):
        '''
        
        Toggle the machine units.
        
        '''
        if self.data.units == "INCHES":
            self.data.units = "MM"
        else:
            self.data.units = "INCHES"
        
        self.unitsBtn.text = self.data.units
    
    def zIn(self):
        '''
        
        Move the z-axis in
        
        '''
        print self.distBtn.text
        self.data.gcode_queue.put("G91 G00 Z" + str(-1*float(self.distBtn.text)) + " G90 ")
    
    def zOut(self):
        '''
        
        Move the z-axis out
        
        '''
        self.data.gcode_queue.put("G91 G00 Z" + str(self.distBtn.text) + " G90 ")
    
    def zero(self):
        '''
        
        Define the z-axis to be currently at height 0
        
        '''
        self.data.gcode_queue.put("G10 Z0 ")
    