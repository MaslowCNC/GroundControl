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
    lineOne = None
    lineTwo = None
    
    sledPointOne    = ObjectProperty([0,0]) #top right corner
    sledPointTwo    = ObjectProperty([0,0]) #top left corner
    sledToolPos     = ObjectProperty([0,0]) #top left corner
    sledMidpointTop = ObjectProperty([0,0])
    
    sledHeight = 130
    sledWidth  = 300
    
    slant = 0
    slantAsString       = StringProperty("Slant: ")
    toolPosAsString     = StringProperty("Pos: ")
    topLengthAsString   = StringProperty("Length: ")
    lengthOfTopBar      = sledWidth
    correctionFactor    = [0,0]
    correctionFactorString = StringProperty("Correction: " + str(correctionFactor))
    errorDist           = 0
    errorDistString     = StringProperty("Error: " + str(errorDist))
    
    
    def initialize(self, lineOne, lineTwo, end, angle):
        self.lineOne = lineOne
        self.lineTwo = lineTwo
        self.angleObject = angle
        self.end = end
        
        self.lineOne.bind(fromPos = self.updateSled)
        self.lineOne.bind(toPos   = self.updateSled)
        self.lineTwo.bind(fromPos = self.updateSled)
        self.lineTwo.bind(toPos   = self.updateSled)
        
        self.updateSled()
    
    
    def updateSled(self, *args):
        
        
        #here we are going to try to find values for distUpLine which will preserve the correct width
        a = self.sledWidth/(math.sqrt(2)*math.sqrt(1-math.cos(math.radians(self.angleObject.angle))))
        print "a"
        print a
        print self.angleObject.angle
        
        
        distUpLine = a
        x = distUpLine/math.sqrt(math.pow(self.lineTwo.slope,2) + 1)
        y = self.lineTwo.slope*x
        
        xDist = self.lineTwo.toPos[0] + x
        yDist = self.lineTwo.toPos[1] + y
        
        self.sledPointOne = (xDist,yDist)
        
        
        x = distUpLine/math.sqrt(math.pow(self.lineOne.slope,2) + 1)
        y = self.lineOne.slope*x
        
        xDist = self.lineTwo.toPos[0] - x
        yDist = self.lineTwo.toPos[1] - y
        
        self.sledPointTwo = (xDist,yDist)
        
        self.lengthOfTopBar = math.sqrt(math.pow((self.sledPointOne[1] - self.sledPointTwo[1]), 2) + math.pow((self.sledPointOne[0] - self.sledPointTwo[0]), 2))
        self.topLengthAsString = "Length: " + str(self.lengthOfTopBar)
        
        try:
            slopeBetweenPoints = ( self.sledPointOne[1]-self.sledPointTwo[1] ) / (self.sledPointOne[0] - self.sledPointTwo[0])
        except:
            pass
        
        
        
        self.slant = math.degrees(math.atan(slopeBetweenPoints))
        self.slantAsString = "Slant: " + str(self.slant)
        
        self.sledMidpointTop[0] = (self.sledPointOne[0]+self.sledPointTwo[0])/2
        self.sledMidpointTop[1] = (self.sledPointOne[1]+self.sledPointTwo[1])/2
        
        
        perpindicularSlope = -10000
        try:
            perpindicularSlope = -1/slopeBetweenPoints
        
        except:
            pass
        
        x = self.sledHeight/math.sqrt(math.pow(perpindicularSlope,2) + 1)
        y = perpindicularSlope*x
        
        slopeSign = math.copysign(1, perpindicularSlope)
        self.sledToolPos[0] = self.sledMidpointTop[0] - slopeSign*x
        self.sledToolPos[1] = self.sledMidpointTop[1] - slopeSign*y
        self.toolPosAsString = "Pos: " + str(self.sledToolPos)
        
        self.correctionFactor[0] = self.sledToolPos[0] - self.lineOne.toPos[0]
        self.correctionFactor[1] = self.sledToolPos[1] - self.lineOne.toPos[1]
        self.correctionFactorString = "Correction: " + str(self.correctionFactor)
        
        self.errorDist = math.sqrt(math.pow(self.correctionFactor[0],2) + math.pow(self.correctionFactor[1],2))
        self.errorDistString     = "Error: " + str(self.errorDist)
        
        
        
        
    
    