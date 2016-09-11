from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class SimulationAngle(FloatLayout):
    
    #scatterObject     = ObjectProperty(None)
    
    angle = NumericProperty(0)
    angleAsString = StringProperty("0")
    lineOne = None
    lineTwo = None
    end = 0
    textPos = ObjectProperty([0,0])
    
    
    
    def initialize(self, lineOne, lineTwo, end):
        self.lineOne = lineOne
        self.lineTwo = lineTwo
        
        self.end = end
        
        self.lineOne.bind(fromPos = self.updateAngle)
        self.lineOne.bind(toPos = self.updateAngle)
        
        self.updateAngle()
    
    def updateAngle(self, *args):
        if self.end == 0:
            self.textPos = self.lineOne.fromPos
        else:
            self.textPos = self.lineOne.toPos
        
        tempAngle = abs(math.degrees(math.atan2((self.lineOne.slope-self.lineTwo.slope),(1+self.lineOne.slope*self.lineTwo.slope))))
        
        if self.end == 1:
            self.angle = 90 + (90-tempAngle)
        else:
            self.angle = tempAngle
        
        self.angleAsString = str(self.angle)
    
    