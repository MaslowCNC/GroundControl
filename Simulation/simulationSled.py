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
    
    sledPointOne = ObjectProperty([0,0]) #top right corner
    sledPointTwo = ObjectProperty([0,0]) #top left corner
    sledHeight = 100
    sledWidth  = 200
    
    slant = 0
    slantAsString = StringProperty("Slant: ")
    
    def initialize(self, lineOne, lineTwo, end, angle):
        self.lineOne = lineOne
        self.lineTwo = lineTwo
        self.angleObject = angle
        self.end = end
        
        self.lineOne.bind(fromPos = self.updateSled)
        self.lineOne.bind(toPos = self.updateSled)
        
        self.updateSled()
    
    
    def updateSled(self, *args):
        
        distUpLine = 100
        x = distUpLine/math.sqrt(math.pow(self.lineTwo.slope,2) + 1)
        y = self.lineTwo.slope*x
        
        print "this"
        print y
        
        xDist = self.lineTwo.toPos[0] + x
        yDist = self.lineTwo.toPos[1] + y
        
        self.sledPointOne = (xDist,yDist)
        
        
        x = distUpLine/math.sqrt(math.pow(self.lineOne.slope,2) + 1)
        y = self.lineOne.slope*x
        
        print y
        
        xDist = self.lineTwo.toPos[0] - x
        yDist = self.lineTwo.toPos[1] - y
        
        self.sledPointTwo = (xDist,yDist)
        
        
        try:
            slopeBetweenPoints = ( self.sledPointOne[1]-self.sledPointTwo[1] ) / (self.sledPointOne[0] - self.sledPointTwo[0])
        except:
            pass
        
        
        
        self.slant = math.degrees(math.atan(slopeBetweenPoints))
        self.slantAsString = "Slant: " + str(self.slant)
        
        
    
    