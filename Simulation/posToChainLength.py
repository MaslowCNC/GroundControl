from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class PosToChainLength(FloatLayout):
    
    lenAString = StringProperty("none")
    lenBString = StringProperty("none")
    
    motorSpacing = 0
    motorHeight = 0
    sledHeight = 130
    sledWidth  = 300
    motorTranslate = 0
    motorLift = 0
    
    posObject = None
    
    def initialize(self, posObject, motorSpacing, motorHeight, motorTranslate, motorLift):
        
        self.posObject = posObject
        self.posObject.bind(sledToolPos = self.update)
    
    def update(self, callback, value):
        self.posToLengths(self.posObject.sledToolPos[0], self.posObject.sledToolPos[1])
    
    def posToLengths(self, xVal, yVal):
        print "pos to len ran"
        print xVal
        print yVal
        