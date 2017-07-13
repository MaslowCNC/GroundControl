from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from kinematics                              import Kinematics
from testPoint                               import TestPoint
from kivy.graphics.transformation            import Matrix

import re
import math

class SimulationCanvas(GridLayout):
    scatterObject     = ObjectProperty(None)
    
    bedWidth           = 2438.4 #8'
    bedHeight          = 1219.2 #4'
    motorLift          = Kinematics.motorOffsetY
    motorTranslate     = (Kinematics.D - bedWidth)/2
    
    motorY = bedHeight + motorLift
    motor2X = bedWidth + motorTranslate
    
    correctKinematics   = Kinematics()
    distortedKinematics = Kinematics()
    
    def initialize(self):
        print "canvas initialized"
        self.motorSpacingError.bind(value=self.onSliderChange)
        self.motorVerticalError.bind(value=self.onSliderChange)
        self.sledMountSpacingError.bind(value=self.onSliderChange)
        self.sledCGError.bind(value=self.onSliderChange)
        
        self.recompute()
        
    def setInitialZoom(self):
        mat = Matrix().scale(.4, .4, 1)
        self.scatterInstance.apply_transform(mat, (0,0))
        
        mat = Matrix().translate(200, 100, 0)
        self.scatterInstance.apply_transform(mat)
    
    def resetSliders(self):
        print "connection made"
        self.motorSpacingError.value = 0
        self.motorVerticalError.value = 0
        self.sledMountSpacingError.value = 0
        self.sledCGError.value = 0
    
    def recompute(self):
        print "recompute"
        
        self.scatterInstance.canvas.clear()
        
        #re-draw 4x8 outline
        self.drawOutline()
        
        testPoint = TestPoint()
        testPoint.initialize(self.scatterInstance.canvas, self.correctKinematics, self.distortedKinematics)
    
    def addPoints(self):
        pass
    
    def onSliderChange(self, *args):
        
        self.distortedKinematics.motorOffsetY = self.correctKinematics.motorOffsetY + self.motorVerticalError.value
        self.distortedKinematics.l = self.correctKinematics.l + self.sledMountSpacingError.value
        self.distortedKinematics.D = self.correctKinematics.D + self.motorSpacingError.value
        
        self.recompute()
    
    def drawOutline(self):
        
        bedWidth  = self.correctKinematics.machineWidth
        bedHeight = self.correctKinematics.machineHeight
        
        with self.scatterInstance.canvas:
            Line(points=(-bedWidth/2, -bedHeight/2, -bedWidth/2, bedHeight/2))
            Line(points=(bedWidth/2, -bedHeight/2, bedWidth/2, bedHeight/2))
            Line(points=(-bedWidth/2, -bedHeight/2, +bedWidth/2, -bedHeight/2))
            Line(points=(-bedWidth/2, bedHeight/2, +bedWidth/2, bedHeight/2))