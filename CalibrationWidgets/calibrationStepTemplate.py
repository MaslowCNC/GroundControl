'''

This is the widget which creates a frame around the calibration process providing infrastructure like the forwards and back buttons.

'''
from   kivy.uix.gridlayout							import   GridLayout
from   kivy.properties								import   ObjectProperty

class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    
    
    pass