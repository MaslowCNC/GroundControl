from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

from kinematics                              import Kinematics

import re
import math

class SimulationSled(FloatLayout):
    
    #scatterObject     = ObjectProperty(None)
    
    angleObject      = None
    leftChain        = None
    rightChain       = None
    
    
    sledHeight = 130
    sledWidth  = 300
    
    toolX           = 0
    toolY           = 0
    
    widthLinePoints  = ObjectProperty([0,0,0,0])
    heightLinePoints = ObjectProperty([0,0,0,0])
    
    initialized         = False
    
    
    def initialize(self, leftChain, rightChain, end):
        self.leftChain = leftChain
        self.rightChain = rightChain
        self.end = end
        
        self.leftChain.bind(fromPos = self.updateSled)
        self.leftChain.bind(toPos   = self.updateSled)
        self.rightChain.bind(fromPos = self.updateSled)
        self.rightChain.bind(toPos   = self.updateSled)
        
        self.kinematics = Kinematics()
        
        self.initialized = True
        
        self.updateSled()
    
    def updateSled(self, *args):
        
        if self.initialized:
            
            self.kinematics.recomputeGeometry()
            self.kinematics.inverse(0,0)
            
            leftChainAttachment  = (self.toolX - self.sledWidth/2, self.toolY + self.sledHeight)
            rightChainAttahcment = (self.toolX + self.sledWidth/2, self.toolY + self.sledHeight)
            
            self.widthLinePoints  = (leftChainAttachment[0], leftChainAttachment[1], rightChainAttahcment[0], rightChainAttahcment[1])
            self.heightLinePoints = (self.toolX, self.toolY, self.toolX, self.toolY + self.sledHeight)
            
            self.leftChain.toPos  = leftChainAttachment
            self.rightChain.toPos = rightChainAttahcment
    
    def setXY(self, x, y):
        
        self.toolX = x
        self.toolY = y
        self.updateSled()