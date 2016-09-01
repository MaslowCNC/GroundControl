from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from simulationLine                          import SimulationLine

import re
import math

class SimulationCanvas(FloatLayout):
    scatterObject     = ObjectProperty(None)
    
    def initialize(self):
        self.chainA.initialize()
        self.chainB.initialize()
        self.lineT.initialize()
        
        
        self.chainA.setEnd(100,200)
        self.chainB.setEnd(400,200)
        self.lineT.setEnd(2946,1439.2)
    
    pass