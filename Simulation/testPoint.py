from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kinematics                              import Kinematics
from kivy.graphics                           import Color, Ellipse, Line

import math

class TestPoint(GridLayout):
    
    xLocation = 0
    yLocation = 0
    
    def initialize(self, targetCanvas, correctKinematics, distortedKinematics): 
        #print "test point initialized"
        self.targetCanvas        = targetCanvas
        self.correctKinematics   = correctKinematics
        self.distortedKinematics = distortedKinematics
        self.bedWidth  = self.correctKinematics.machineWidth
        self.bedHeight = self.correctKinematics.machineHeight

        
    
    def setTarget(self, xTarget, yTarget):
        self.xLocation = xTarget
        self.yLocation = yTarget
    
    def plotPoint(self, correctPosX, correctPosY, *args):
        #print "plotting point"
        radius = 5
        
        #take the position, translate it to chain lengths
        chainALength, chainBLength = self.correctKinematics.inverse(correctPosX, correctPosY)
        #print chainALength
        #print chainBLength
        
        #then back into XY coordinates using the correct kinematics
        correctPosX, correctPosY = self.correctKinematics.forward(chainALength, chainBLength)
        #print "pos:"
        #print correctPosX
        #print correctPosY
        
        #then back into XY coordinateness using the distorted kinematics
        distortedPosX, distortedPosY = self.distortedKinematics.forward(chainALength, chainBLength)
        #print "distorted Pos"
        #print distortedPosX
        #print distortedPosY
        
        with self.targetCanvas:
            Color(0, 1, 0)
            Line(circle=(correctPosX+self.bedWidth/2, correctPosY+self.bedHeight/2, radius))
            Color(1, 0, 0)
            Line(circle=(distortedPosX+self.bedWidth/2, distortedPosY+self.bedHeight/2, radius))
        
        distortedPoint = (distortedPosX, distortedPosY)
        correctPoint   = (correctPosX, correctPosY)
        
        return correctPoint, distortedPoint
