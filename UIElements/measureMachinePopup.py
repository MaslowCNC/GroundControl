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
    
    def LeftCW(self):
        print "left CW"
        self.data.gcode_queue.put("G91 \nB09 L.5 \nG90 ")
    
    def LeftCCW(self):
        print "left CCW"
        self.data.gcode_queue.put("G91 \nB09 L-.5 \nG90 ")
        
    def RightCW(self):
        print "right CW"
        self.data.gcode_queue.put("G91 \nB09 R-.5 \nG90 ")
    
    def RightCCW(self):
        print "right CCW"
        self.data.gcode_queue.put("G91 \nB09 R.5 \nG90 ")
    
    