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
    
    def updateGcode(self):
        print "this ran"
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            Line(points = (0, 0, 100, 100))
     