from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class SimulationLine(FloatLayout):
    
    #scatterObject     = ObjectProperty(None)
    
    color           = (1,1,1)
    fromPos         = ObjectProperty([0,0])
    toPos           = ObjectProperty([0,0])
    lengthAsString  = StringProperty("0")
    length          = 0
    
    def initialize(self):
        self.updateLength()
        self.bind(fromPos = self.updateLength)
        self.bind(toPos = self.updateLength)
    
    def updateLength(self, *args):
        self.length = math.sqrt(math.pow((self.fromPos[0] - self.toPos[0]),2) + math.pow((self.fromPos[1] - self.toPos[1]),2))
        self.lengthAsString = str(self.length)
    
    def setStart(self,x,y):
        self.fromPos = [x,y]
    
    def setEnd(self,x,y):
        self.toPos = [x,y]
    
    