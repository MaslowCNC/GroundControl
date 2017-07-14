from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from kinematics                              import Kinematics
from testPoint                               import TestPoint
from kivy.graphics.transformation            import Matrix
from kivy.clock                              import Clock
from functools                               import partial

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
        self.vertBitDist.bind(value=self.onSliderChange)
        
        #scale it down to fit on the screen
        self.scatterInstance.apply_transform(Matrix().scale(.3, .3, 1))
        
        
        mat = Matrix().translate(500, 500, 0)
        self.scatterInstance.apply_transform(mat)
        
        
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
        self.vertBitDist.value = 0
    
    def recompute(self):
        print "recompute"
        
        #clear the canvas to redraw
        self.scatterInstance.canvas.clear()
        
        #re-draw 4x8 outline
        self.drawOutline()
        
        leftRigthBound  = int(self.correctKinematics.machineWidth/2)
        topBottomBound  = int(self.correctKinematics.machineHeight/2)
        
        self.testPointGenerator = TestPoint()
        self.testPointGenerator.initialize(self.scatterInstance.canvas, self.correctKinematics, self.distortedKinematics)
        
        self.listOfPointsToPlot = []
        self.listOfPointsPlotted = []
        self.listOfDistortedPoints = []
        self.pointIndex = 0
        horizontalStepSize = (2*leftRigthBound)/12
        verticalStepSize   = (2*topBottomBound)/7
        self.verticalPoints   = range(topBottomBound, -topBottomBound, -200)
        self.horizontalPoints = range(-leftRigthBound, leftRigthBound, horizontalStepSize)
        
        #self.doSpecificCalculation()
        
        for j in self.verticalPoints:
            for i in self.horizontalPoints:
                point = (i,j)
                self.listOfPointsToPlot.append(point)
                
        self.plotNextPoint()

    def plotNextPoint(self, *args):
        point = self.listOfPointsToPlot[self.pointIndex]
        self.pointIndex = self.pointIndex + 1
        xValue = point[0]
        yValue = point[1]
        
        pointPlotted, distortedPoint = self.testPointGenerator.plotPoint(xValue, yValue)
        self.listOfPointsPlotted.append(pointPlotted)
        self.listOfDistortedPoints.append(distortedPoint)
        
        if self.pointIndex < len(self.listOfPointsToPlot):
            Clock.schedule_once(self.plotNextPoint)
        else:
            self.drawLines()
        
    def drawLines(self):
        
        bedWidth  = self.correctKinematics.machineWidth
        bedHeight = self.correctKinematics.machineHeight
        
        #draw distorted points
        
        
        for i in range(0, len(self.verticalPoints)):
            points = []
            
            for j in range(0,len(self.horizontalPoints)):
                point = self.listOfDistortedPoints[j + i*len(self.horizontalPoints)]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)
            
            with self.scatterInstance.canvas:
                Color(1,0,0)
                Line(points=points)
        
        for i in range(0, len(self.horizontalPoints)):
            points = []
            for j in range(0,len(self.listOfDistortedPoints),len(self.horizontalPoints)):
                point = self.listOfDistortedPoints[j+i]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)
            
            
            with self.scatterInstance.canvas:
                Color(1,0,0)
                Line(points=points)
        
        #draw regular lines
        
        for i in range(0, len(self.verticalPoints)):
            points = []
            
            for j in range(0,len(self.horizontalPoints)):
                point = self.listOfPointsPlotted[j + i*len(self.horizontalPoints)]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)
            
            with self.scatterInstance.canvas:
                Color(0,1,0)
                Line(points=points)
        
        for i in range(0, len(self.horizontalPoints)):
            points = []
            for j in range(0,len(self.listOfPointsPlotted),len(self.horizontalPoints)):
                point = self.listOfPointsPlotted[j+i]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)
            
            
            with self.scatterInstance.canvas:
                Color(0,1,0)
                Line(points=points)
        
    def addPoints(self):
        pass
    
    def doSpecificCalculation(self):
        print "The horizontal measurement of a centered 48 inch long part cut low down on the sheet is: "
        
        lengthMM = 1219.2
        
        pointPlotted1, distortedPoint1 = self.testPointGenerator.plotPoint(-lengthMM/2, -200)
        pointPlotted2, distortedPoint2 = self.testPointGenerator.plotPoint(lengthMM/2, -200)
        
        print distortedPoint2[0] - distortedPoint1[0]
        print "Error: " + str(lengthMM - (distortedPoint2[0] - distortedPoint1[0]))
    
    def onSliderChange(self, *args):
        
        self.distortedKinematics.motorOffsetY = self.correctKinematics.motorOffsetY + self.motorVerticalError.value
        self.motorVerticalErrorLabel.text = "Motor Vertical\nError: " + str(int(self.motorVerticalError.value)) + "mm"
        
        self.distortedKinematics.l = self.correctKinematics.l + self.sledMountSpacingError.value
        self.sledMountSpacingErrorLabel.text = "Sled Mount\nSpacing Error: " + str(int(self.sledMountSpacingError.value)) + "mm"
        
        self.distortedKinematics.D = self.correctKinematics.D + self.motorSpacingError.value
        self.motorSpacingErrorLabel.text = "Motor Spacing\nError: " + str(int(self.motorSpacingError.value)) + "mm"
        
        self.distortedKinematics.s = self.correctKinematics.s + self.vertBitDist.value
        self.vertBitDistLabel.text = "Vert Dist To\nBit Error: " + str(int(self.vertBitDist.value)) + "mm"
        
        self.distortedKinematics.recomputeGeometry()
    
    def drawOutline(self):
        
        bedWidth  = self.correctKinematics.machineWidth
        bedHeight = self.correctKinematics.machineHeight
        
        with self.scatterInstance.canvas:
            Line(points=(0, 0, 0, bedHeight))
            Line(points=(0, bedHeight, bedWidth, bedHeight))
            Line(points=(bedWidth, bedHeight, bedWidth, 0))
            Line(points=(bedWidth, 0, 0, 0))
            
    def on_touch_up(self, touch):
        
        if touch.is_mouse_scrolling:
            self.zoomCanvas(touch)
    
    def zoomCanvas(self, touch):
        if touch.is_mouse_scrolling:
            scaleFactor = .1
            
            if touch.button == 'scrollup':
                mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor = touch.pos)
            elif touch.button == 'scrolldown':
                mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor = touch.pos)
