from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from .kinematics                              import Kinematics
from kivy.graphics                           import Color, Ellipse, Line

import math

class TestPoint(GridLayout):

    xLocation = 0
    yLocation = 0

    def initialize(self, targetCanvas, correctKinematics, distortedKinematics):
        
        self.targetCanvas        = targetCanvas
        self.correctKinematics   = correctKinematics
        self.distortedKinematics = distortedKinematics
        self.bedWidth  = self.correctKinematics.machineWidth
        self.bedHeight = self.correctKinematics.machineHeight



    def setTarget(self, xTarget, yTarget):
        self.xLocation = xTarget
        self.yLocation = yTarget

    def plotPoint(self, correctPosX, correctPosY, *args):
        
        radius = 5
        self.xLocation = correctPosX
        self.yLocation = correctPosY

        #take the position, translate it to chain lengths
        chainALength, chainBLength = self.correctKinematics.inverse(correctPosX, correctPosY)

        #then back into XY coordinates using the correct kinematics
        correctPosX, correctPosY = self.correctKinematics.forward(chainALength, chainBLength)

        #then back into XY coordinateness using the distorted kinematics
        distortedPosX, distortedPosY = self.distortedKinematics.forward(chainALength, chainBLength)

        with self.targetCanvas:
            Color(0, 0, 1)
            Line(circle=(self.xLocation+self.bedWidth/2, self.yLocation+self.bedHeight/2, radius-3))
            Color(0, 1, 0)
            Line(circle=(correctPosX+self.bedWidth/2, correctPosY+self.bedHeight/2, radius-2))
            Color(1, 0, 0)
            Line(circle=(distortedPosX+self.bedWidth/2, distortedPosY+self.bedHeight/2, radius))

        #print 'ideal, {:+7.2f}, {:+7.2f}  pos, {:+7.2f}, {:+7.2f}  Error, {:7.2f}, {:7.2f}  Distortion, {:7.2f}, {:7.2f}'.format(self.xLocation,self.yLocation,correctPosX,correctPosY,self.xLocation-correctPosX,self.yLocation-correctPosY,correctPosX-distortedPosX,correctPosY-distortedPosY)
        distortedPoint = (distortedPosX, distortedPosY)
        correctPoint   = (correctPosX, correctPosY)

        return correctPoint, distortedPoint
