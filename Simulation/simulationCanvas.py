from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty, BooleanProperty
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
    kinematicsType      = 'Quadrilateral'
    
    isQuadKinematics    = BooleanProperty(True)

    def initialize(self):
        
        self.motorSpacingError.bind(value=self.onSliderChange)
        self.motorVerticalError.bind(value=self.onSliderChange)
        self.sledMountSpacingError.bind(value=self.onSliderChange)
        self.vertBitDist.bind(value=self.onSliderChange)
        self.leftChainOffset.bind(value=self.onSliderChange)
        self.rightChainOffset.bind(value=self.onSliderChange)
        self.rotationRadiusOffset.bind(value=self.onSliderChange)

        self.vertCGDist.bind(value=self.onSliderChange)
        self.gridSize.bind(value=self.onSliderChange)
        
        Clock.schedule_once(self.moveToCenter, 3)
        
        #start with our current kinematics type
        self.kinematicsSelect.text = self.data.config.get('Advanced Settings', 'kinematicsType')
          
        self.recompute()
    
    def moveToCenter(self, *args):
        
        
        #This moves the simulation onto the screen, I would love if it were centered
        #but for now it doesn't adapt to screen size (Window.width, Window.height)
        
        moveVertical = self.bedHeight/1.4
        moveHorizontal = self.bedWidth/1.4
        
        mat = Matrix().translate(moveHorizontal, moveVertical, 0)
        self.scatterInstance.apply_transform(mat)
        
        #scale it down to fit on the screen
        self.scatterInstance.apply_transform(Matrix().scale(.3, .3, 1))

    def setInitialZoom(self):
        mat = Matrix().scale(.4, .4, 1)
        self.scatterInstance.apply_transform(mat, (0,0))

        mat = Matrix().translate(200, 100, 0)
        self.scatterInstance.apply_transform(mat)

    def resetSliders(self):
        
        self.motorSpacingError.value = 0
        self.motorVerticalError.value = 0
        self.sledMountSpacingError.value = 0
        self.vertBitDist.value = 0
        self.vertCGDist.value = 0
        self.leftChainOffset.value = 0
        self.rightChainOffset.value = 0
        self.rotationRadiusOffset.value = 0
        self.gridSize.value=300

    def recompute(self):
        

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
        self.verticalPoints   = range(int(int(topBottomBound/self.gridSize.value)*self.gridSize.value), -topBottomBound, -1 * int(self.gridSize.value))
        self.horizontalPoints = range(int(int(leftRigthBound/self.gridSize.value)*self.gridSize.value), -leftRigthBound, -1 * int(self.gridSize.value))

        self.doSpecificCalculation()
        self.scatterInstance.canvas.clear()

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

        #draw ideal points


        for i in range(0, len(self.verticalPoints)):
            points = []

            for j in range(0,len(self.horizontalPoints)):
                point = self.listOfPointsToPlot[j + i*len(self.horizontalPoints)]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)

            with self.scatterInstance.canvas:
                Color(0,0,1)
                Line(points=points)

        for i in range(0, len(self.horizontalPoints)):
            points = []
            for j in range(0,len(self.listOfPointsToPlot),len(self.horizontalPoints)):
                point = self.listOfPointsToPlot[j+i]
                points.append(point[0]+self.bedWidth/2)
                points.append(point[1]+self.bedHeight/2)


            with self.scatterInstance.canvas:
                Color(0,0,1)
                Line(points=points)

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
        
        lengthMM = 800

        #horizontal measurement 
        pointPlotted1, distortedPoint1 = self.testPointGenerator.plotPoint(-lengthMM/2, 0)
        pointPlotted2, distortedPoint2 = self.testPointGenerator.plotPoint(lengthMM/2,  0)
        
        #vertical measurement
        pointPlotted3, distortedPoint3 = self.testPointGenerator.plotPoint(0, lengthMM/2)
        pointPlotted4, distortedPoint4 = self.testPointGenerator.plotPoint(0, -lengthMM/2)
        
        printString = "An 800mm square centered on the sheet is distorted\n%.4fmm horizontally, and %.4fmm vertically." % ( (lengthMM - (distortedPoint2[0] - distortedPoint1[0])), (lengthMM - (distortedPoint3[1] - distortedPoint4[1])))
        
        lengthMM = 1905/2
        
        pointPlotted1, distortedPoint1 = self.testPointGenerator.plotPoint(-lengthMM/2, -400)
        pointPlotted2, distortedPoint2 = self.testPointGenerator.plotPoint(lengthMM/2,  -400)
        
        printString1 = printString + "\n\nThe triangular calibration test is off by %.4fmm." % ((lengthMM - (distortedPoint2[0] - distortedPoint1[0])))
        
        
        
        
        
        lengthMM = 800
        xOffset = 1100 - lengthMM/2
        yOffset = 500  - lengthMM/2
        
        #horizontal measurement 
        pointPlotted1, distortedPoint1 = self.testPointGenerator.plotPoint(-lengthMM/2, yOffset)
        pointPlotted2, distortedPoint2 = self.testPointGenerator.plotPoint(lengthMM/2,  yOffset)
        
        #vertical measurement
        pointPlotted3, distortedPoint3 = self.testPointGenerator.plotPoint(xOffset, lengthMM/2)
        pointPlotted4, distortedPoint4 = self.testPointGenerator.plotPoint(xOffset, -lengthMM/2)
        
        printString = "An 800mm square in the top corner on the sheet is distorted\n%.4fmm horizontally, and %.4fmm vertically." % ( (lengthMM - (distortedPoint2[0] - distortedPoint1[0])), (lengthMM - (distortedPoint3[1] - distortedPoint4[1])))
        
        lengthMM = 800
        xOffset = 1100 - lengthMM/2
        yOffset = 500  - lengthMM/2
        
        #horizontal measurement 
        pointPlotted1, distortedPoint1 = self.testPointGenerator.plotPoint(-lengthMM/2, -yOffset)
        pointPlotted2, distortedPoint2 = self.testPointGenerator.plotPoint(lengthMM/2,  -yOffset)
        
        #vertical measurement
        pointPlotted3, distortedPoint3 = self.testPointGenerator.plotPoint(xOffset, lengthMM/2)
        pointPlotted4, distortedPoint4 = self.testPointGenerator.plotPoint(xOffset, -lengthMM/2)
        
        printString2 = printString + "\n\nAn 800mm square in the bottom corner on the sheet is distorted\n%.4fmm horizontally, and %.4fmm vertically." % ( (lengthMM - (distortedPoint2[0] - distortedPoint1[0])), (lengthMM - (distortedPoint3[1] - distortedPoint4[1])))
        
        #calculate "Calibration Benchmark Score"

        #dimensions used in calibration cuts
        scoreXMM   = 1905.0 
        scoreYMM   = 900.0
        scoreBoxMM = 100.0

        #plot horizontal measurement 
        pointPlotted1h, distortedPoint1h = self.testPointGenerator.plotPoint(-scoreXMM/2.0,  scoreYMM/2.0)
        pointPlotted2h, distortedPoint2h = self.testPointGenerator.plotPoint( scoreXMM/2.0,  scoreYMM/2.0)
        errHTop = abs(scoreXMM - abs(distortedPoint1h[0] - distortedPoint2h[0]))
        pointPlotted3h, distortedPoint3h = self.testPointGenerator.plotPoint(-scoreXMM/2.0,           0.0)
        pointPlotted4h, distortedPoint4h = self.testPointGenerator.plotPoint( scoreXMM/2.0,           0.0)
        errHMid = abs(scoreXMM - abs(distortedPoint3h[0] - distortedPoint4h[0]))
        pointPlotted5h, distortedPoint5h = self.testPointGenerator.plotPoint(-scoreXMM/2.0, -scoreYMM/2.0)
        pointPlotted6h, distortedPoint6h = self.testPointGenerator.plotPoint( scoreXMM/2.0, -scoreYMM/2.0)
        errHBtm = abs(scoreXMM - abs(distortedPoint5h[0] - distortedPoint6h[0]))

        # print  "errHTop  "  + str(errHTop)
        # print  "errHMid  "  + str(errHMid)
        # print  "errHBtm  "  + str(errHBtm)

        #plot vertical measurements
        pointPlotted1v, distortedPoint1v = self.testPointGenerator.plotPoint(-scoreXMM/2.0,  scoreYMM/2.0)
        pointPlotted2v, distortedPoint2v = self.testPointGenerator.plotPoint(-scoreXMM/2.0, -scoreYMM/2.0)
        errVLft = abs(scoreYMM - abs(distortedPoint1v[1] - distortedPoint2v[1]))
        pointPlotted3v, distortedPoint3v = self.testPointGenerator.plotPoint(          0.0,  scoreYMM/2.0)
        pointPlotted4v, distortedPoint4v = self.testPointGenerator.plotPoint(          0.0, -scoreYMM/2.0)
        errVMid = abs(scoreYMM - abs(distortedPoint3v[1] - distortedPoint4v[1]))
        pointPlotted5v, distortedPoint5v = self.testPointGenerator.plotPoint(scoreXMM /2.0,  scoreYMM/2.0)
        pointPlotted6v, distortedPoint6v = self.testPointGenerator.plotPoint(scoreXMM /2.0, -scoreYMM/2.0)
        errVRht = abs(scoreYMM - abs(distortedPoint5v[1] - distortedPoint6v[1]))

        # print  "errVLft  "  + str(errVLft)
        # print  "errVMid  "  + str(errVMid)
        # print  "errVRht  "  + str(errVRht)

        #combine the two averages for the first part of the cmScore
        cmScoreBig = (errHTop + errHMid + errHBtm + errVLft + errVMid + errVRht) / 6.0

        #plot box measurements
        pointPlotted0b, distortedPoint0b = self.testPointGenerator.plotPoint(-scoreXMM  /2.0,               scoreYMM  /2.0             )
        pointPlotted1b, distortedPoint1b = self.testPointGenerator.plotPoint(-scoreXMM  /2.0 + scoreBoxMM,  scoreYMM  /2.0 - scoreBoxMM)
        pointPlotted2b, distortedPoint2b = self.testPointGenerator.plotPoint(-scoreXMM  /2.0,              -scoreYMM  /2.0             )
        pointPlotted3b, distortedPoint3b = self.testPointGenerator.plotPoint(-scoreXMM  /2.0 + scoreBoxMM, -scoreYMM  /2.0 + scoreBoxMM)
        pointPlotted4b, distortedPoint4b = self.testPointGenerator.plotPoint(-scoreBoxMM/2.0,               scoreBoxMM/2.0             )
        pointPlotted5b, distortedPoint5b = self.testPointGenerator.plotPoint( scoreBoxMM/2.0,              -scoreBoxMM/2.0             )
        pointPlotted6b, distortedPoint6b = self.testPointGenerator.plotPoint( scoreXMM  /2.0,               scoreYMM  /2.0             )
        pointPlotted7b, distortedPoint7b = self.testPointGenerator.plotPoint( scoreXMM  /2.0 - scoreBoxMM,  scoreYMM  /2.0 - scoreBoxMM)
        pointPlotted8b, distortedPoint8b = self.testPointGenerator.plotPoint( scoreXMM  /2.0,              -scoreYMM  /2.0             )
        pointPlotted9b, distortedPoint9b = self.testPointGenerator.plotPoint( scoreXMM  /2.0 - scoreBoxMM, -scoreYMM  /2.0 + scoreBoxMM)

        #calculate second half of "Calibration Benchmark Score" here, X-directon
        scoreBoxX1 = abs(scoreBoxMM - abs(distortedPoint0b[0] - distortedPoint1b[0]))
        scoreBoxX2 = abs(scoreBoxMM - abs(distortedPoint2b[0] - distortedPoint3b[0]))
        scoreBoxX3 = abs(scoreBoxMM - abs(distortedPoint4b[0] - distortedPoint5b[0]))
        scoreBoxX4 = abs(scoreBoxMM - abs(distortedPoint6b[0] - distortedPoint7b[0]))
        scoreBoxX5 = abs(scoreBoxMM - abs(distortedPoint8b[0] - distortedPoint9b[0]))
        scoreBoxX = (scoreBoxX1 + scoreBoxX2 + scoreBoxX3 + scoreBoxX4 + scoreBoxX5)/ 5.0

        #calculate second half of "Calibration Benchmark Score" here, Y-directon
        scoreBoxY1 = abs(scoreBoxMM - abs(distortedPoint0b[1] - distortedPoint1b[1]))
        scoreBoxY2 = abs(scoreBoxMM - abs(distortedPoint2b[1] - distortedPoint3b[1]))
        scoreBoxY3 = abs(scoreBoxMM - abs(distortedPoint4b[1] - distortedPoint5b[1]))
        scoreBoxY4 = abs(scoreBoxMM - abs(distortedPoint6b[1] - distortedPoint7b[1]))
        scoreBoxY5 = abs(scoreBoxMM - abs(distortedPoint8b[1] - distortedPoint9b[1]))
        scoreBoxY = (scoreBoxY1 + scoreBoxY2 + scoreBoxY3 + scoreBoxY4 + scoreBoxY5)/ 5.0

        # print str(scoreBoxX1) + "   " + str(scoreBoxY1)
        # print str(scoreBoxX2) + "   " + str(scoreBoxY2)
        # print str(scoreBoxX3) + "   " + str(scoreBoxY3)
        # print str(scoreBoxX4) + "   " + str(scoreBoxY4)
        # print str(scoreBoxX5) + "   " + str(scoreBoxY5)

        #combine the two averages for the second part of the cmScore
        cmScoreBox = (scoreBoxX + scoreBoxY) / 2.0

        printString1 = printString1 + "\r\n\r\nThe Calibration Benchmark Score is  %.3f - %.3f" % (cmScoreBig,cmScoreBox)

        self.machineLabel1.text = printString1
        self.machineLabel2.text = printString2

    
    def setKinematics(self, kinematicsType):
        
        if kinematicsType == "Quadrilateral":
            self.isQuadKinematics = True
            self.distortedKinematics.isQuadKinematics = True
            self.correctKinematics.isQuadKinematics = True
        else:
            self.isQuadKinematics = False
            self.distortedKinematics.isQuadKinematics = False
            self.correctKinematics.isQuadKinematics = False
    
    def onSliderChange(self, *args):

        self.distortedKinematics.motorOffsetY = self.correctKinematics.motorOffsetY + self.motorVerticalError.value
        self.motorVerticalErrorLabel.text = "Motor Vertical\nError: " + "%.2f" % self.motorVerticalError.value + "mm"

        self.distortedKinematics.l = self.correctKinematics.l + self.sledMountSpacingError.value
        self.sledMountSpacingErrorLabel.text = "Sled Mount\nSpacing Error: " + "%.2f" % self.sledMountSpacingError.value + "mm"

        self.distortedKinematics.D = self.correctKinematics.D + self.motorSpacingError.value
        self.motorSpacingErrorLabel.text = "Motor Spacing\nError: " + "%.2f" % self.motorSpacingError.value + "mm"

        self.distortedKinematics.s = self.correctKinematics.s + self.vertBitDist.value
        self.vertBitDistLabel.text = "Vert Dist To\nBit Error: " + "%.2f" % self.vertBitDist.value + "mm"

        self.distortedKinematics.h3 = self.correctKinematics.h3 + self.vertCGDist.value
        self.vertCGDistLabel.text = "Vert Dist\nBit to CG Error: " + "%.2f" % self.vertCGDist.value + "mm"

        self.distortedKinematics.chain1Offset = int(self.leftChainOffset.value)
        self.leftChainOffsetLabel.text = "Left Chain\nSlipped Links: " + "%.2f" % self.leftChainOffset.value + "links"

        self.distortedKinematics.chain2Offset = int(self.rightChainOffset.value)
        self.rightChainOffsetLabel.text = "Right Chain\nSlipped Links: " + "%.2f" % self.rightChainOffset.value + "links"
        
        self.distortedKinematics.rotationDiskRadius = self.correctKinematics.rotationDiskRadius + self.rotationRadiusOffset.value
        self.rotationRadiusLabel.text = "Rotation Radius\nSpacing Error: " + "%.2f" % self.rotationRadiusOffset.value + "mm"
        
        #self.machineLabel.text = "distance between sled attachments ideal: "+str(self.correctKinematics.l)+" actual: "+str(self.distortedKinematics.l)+"mm\nvertical distance between sled attachments and bit ideal: "+str(self.correctKinematics.s)+" actual: "+str(self.distortedKinematics.s)+"mm\nvertical distance between sled attachments and CG ideal: "+str(self.correctKinematics.h3+self.correctKinematics.s)+" actual: "+str(self.distortedKinematics.h3+self.distortedKinematics.s)+"mm\ndistance between motors ideal: "+str(self.correctKinematics.D)+" actual: "+str(self.distortedKinematics.D)+"mm"

        self.gridSizeLabel.text = "Grid Size: "+str(int(self.gridSize.value))+"mm"

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
