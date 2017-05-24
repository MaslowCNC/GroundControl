from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class SimulationSled(FloatLayout):
    
    #scatterObject     = ObjectProperty(None)
    
    angleObject   = None
    leftChain = None
    rightChain = None
    
    sledPointOne    = ObjectProperty([0,0]) #top right corner
    sledPointTwo    = ObjectProperty([0,0]) #top left corner
    sledToolPos     = ObjectProperty([0,0]) #top left corner
    sledMidpointTop = ObjectProperty([0,0])
    bottomLeft      = ObjectProperty([0,0])
    bottomRight     = ObjectProperty([0,0])
    
    sledHeight = 130
    sledWidth  = 300
    
    toolX           = 0
    toolY           = 0
    
    slant = 0
    slantAsString       = StringProperty("Slant: ")
    toolPosAsString     = StringProperty("Pos: ")
    topLengthAsString   = StringProperty("Length: ")
    lengthOfTopBar      = sledWidth
    correctionFactor    = [0,0]
    correctionFactorString = StringProperty("Correction: " + str(correctionFactor))
    errorDist           = 0
    errorDistString     = StringProperty("Error: " + str(errorDist))
    
    initialized         = False
    
    
    def initialize(self, leftChain, rightChain, end, angle):
        self.leftChain = leftChain
        self.rightChain = rightChain
        self.angleObject = angle
        self.end = end
        
        self.leftChain.bind(fromPos = self.updateSled)
        self.leftChain.bind(toPos   = self.updateSled)
        self.rightChain.bind(fromPos = self.updateSled)
        self.rightChain.bind(toPos   = self.updateSled)
        
        self.initialized = True
        
        self.updateSled()
    
    
    def updateSled(self, *args):
        
        if self.initialized:
            
            leftChainAttachment  = (self.toolX - self.sledWidth/2, self.toolY + self.sledHeight)
            rightChainAttahcment = (self.toolX + self.sledWidth/2, self.toolY + self.sledHeight)
            
            print self.toolX
            print self.sledWidth/2
            
            self.leftChain.toPos  = leftChainAttachment
            self.rightChain.toPos = rightChainAttahcment
            
    
    
    def setXY(self, x, y):
        
        self.toolX = x
        self.toolY = y
        self.updateSled()