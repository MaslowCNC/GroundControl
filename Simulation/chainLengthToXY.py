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
        
        La = lengthA
        Lb = lengthB
        Ax = 0
        Ay = 0
        Bx = self.motorSpacing
        By = 0
        b  = self.sledWidth
        h  = self.sledHeight
        
        thetaCAB = math.acos((pow(La,2)+pow(Bx,2)-pow(Lb,2))/(2*La*Bx))
        
        Cx = La*(pow(La,2)+pow(Bx,2)-pow(Lb,2))/(2*La*Bx)
        Cy = La*math.sin(math.acos((pow(La,2)+pow(Bx,2)-pow(Lb,2))/(2*La*Bx)))
        
        thetaACB = math.acos((pow(La,2)+pow(Lb,2)-pow(Bx,2))/(2*La*Lb))
        
        lCD = b//(math.sqrt(2)*math.sqrt(1-math.cos(thetaACB)))
        mAC = Cy/Cx
        
        Dx = Cx - lCD/math.sqrt(math.pow(mAC,2) + 1)
        Dy = mAC*Dx
        
        mBC = Cy/(Cx-Bx)
        
        Ex = Cx + lCD/math.sqrt(math.pow(mBC,2) + 1)
        Ey = mBC*(Ex - Bx)
        
        Mx = (Dx + Ex)/2
        My = (Dy + Ey)/2
        
        try:
            mMF = (Ex-Dx)/(Dy-Ey)
            Fx = Mx + (mMF/abs(mMF))*(h/math.sqrt(pow(mMF,2) + 1))
            Fy = My - mMF*(Mx-Fx)
            print mMF*(Mx-Fx)
        except:
            Fx = Mx
            Fy = My + h
        
        
        print h
        
        
        return Fx-self.motorTranslate , self.motorHeight - Fy