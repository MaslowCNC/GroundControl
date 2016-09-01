from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class SimulationLine(FloatLayout):
    
    #scatterObject     = ObjectProperty(None)
    
    color   = (1,1,1)
    fromPos = (0,0)
    toPos   = (100, 100)