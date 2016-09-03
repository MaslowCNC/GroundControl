from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class ChainLengthtoXY(FloatLayout):
    
    xVal = StringProperty("not initialized")
    yVal = StringProperty("not Initialized")
    
    motorSpacing = 0
    motorHeight = 0
    sledHeight = 130
    sledWidth  = 300
    motorTranslate = 0
    motorLift = 0
    
    lengthAObject = None
    lengthBObject = None
    
    def initialize(self, lenA, lenB, motorSpacing, motorHeight, motorTranslate, motorLift):
        self.xVal = "initialized"
        self.yVal = "initialized"
        
        self.motorSpacing = motorSpacing
        self.motorHeight = motorHeight
        
        self.lengthAObject = lenA
        self.lengthBObject = lenB
        
        self.motorTranslate = motorTranslate
        self.motorLift = motorLift
        
        self.lengthAObject.bind(fromPos = self.update)
        self.lengthBObject.bind(toPos = self.update)
        
    def update(self, callback, value):
        self.xVal = "1"
        self.yVal = "2"
        
        x, y = self.chainLengthstoxy(self.lengthAObject.length, self.lengthBObject.length)
        
        self.xVal = str(x)
        self.yVal = str(y)
        
        
    def chainLengthstoxy(self, lengthA, lengthB):
        #find the top angle
        
        a = self.motorSpacing
        b = lengthA
        c = lengthB
        
        theta = math.acos((math.pow(a,2)+math.pow(b,2)-math.pow(c,2))/(2*a*b))
        
        #find the tip of the triangle
        
        tipX = lengthA*math.cos(theta)
        tipY = lengthA*math.sin(theta)
        
        #find the line slopes
        lineASlope = -tipY/tipX
        lineBSlope = tipY/(self.motorSpacing - tipX)
        
        
        #convert to real worl cordinates
        tipX =  tipX - self.motorTranslate
        tipY =  self.motorHeight - (tipY)
        
        #find the angle between the two lines
        c = self.motorSpacing
        a = lengthA
        b = lengthB
        
        theta = math.acos((math.pow(a,2)+math.pow(b,2)-math.pow(c,2))/(2*a*b))
        
        #find the distance from the tip to the cross line
        lengthFromTip = self.sledWidth/(math.sqrt(2)*math.sqrt(1-math.cos(theta)))
        
        
        #find the two points where the distance is the width of the sled
        x = lengthFromTip/math.sqrt(math.pow(lineASlope,2) + 1)
        y = lineASlope*x
        pointOne = (tipX - x,tipY - y)
        
        x = lengthFromTip/math.sqrt(math.pow(lineBSlope,2) + 1)
        y = lineBSlope*x
        pointTwo = (tipX + x,tipY + y)
        
        
        #find the slope of the line
        
        try:
            slope = -1/((pointOne[1]-pointTwo[1])/(pointOne[0]-pointTwo[0]))
        except:
            slope = -1000000000
        
        #find the midpoint
        
        midpoint = ((pointOne[0]+pointTwo[0])/2, (pointOne[1]+pointTwo[1])/2)
        
        #find the point sled width down from the mid point
        
        x = self.sledHeight/math.sqrt(math.pow(slope,2) + 1)
        y = slope*x
        
        slopeSign = math.copysign(1, slope)
        yPos = midpoint[0] - slopeSign*x
        xPos = midpoint[1] - slopeSign*y
        
        return xPos, yPos