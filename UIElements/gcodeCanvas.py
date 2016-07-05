'''

This module provides a UI element which can display gcode on a Kivy canvas element. It also provides panning 
and zooming features. It was not originally written as a stand alone module which might create some weirdness.

'''

from kivy.uix.floatlayout     import FloatLayout
from kivy.properties          import NumericProperty, ObjectProperty
from kivy.graphics            import Color, Ellipse, Line
from kivy.uix.scatter         import Scatter

import re
import math

class GcodeCanvas(FloatLayout):
    
    scatterObject = ObjectProperty(None)
    
    def initialzie(self):
        print "gcode canvas initialized"
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            
            #create the position indicator
            indicatorSize = 20
            Line(points = (-indicatorSize, -indicatorSize, indicatorSize, indicatorSize))
            Line(points = (indicatorSize, -indicatorSize, -indicatorSize, indicatorSize))
            Line(circle=(0, 0, indicatorSize))
            
            #create the axis lines
            crossLineLength = 10000
            Line(points = (-crossLineLength,0,crossLineLength,0), dash_offset = 5)
            Line(points = (0, -crossLineLength,0,crossLineLength), dash_offset = 5)
            
     