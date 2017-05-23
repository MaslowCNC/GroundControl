from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from simulationLine                          import SimulationLine
from simulationAngle                         import SimulationAngle
from simulationSled                          import SimulationSled
from chainLengthToXY                         import ChainLengthtoXY
from posToChainLength                        import PosToChainLength
from kivy.graphics.transformation            import Matrix

import re
import math

class SimulationCanvas(FloatLayout):
    scatterObject     = ObjectProperty(None)
    
    motorLift          = 220
    motorTranslate     = 258.8
    bedWidth           = 2438.4 #8'
    bedHeight          = 1219.2 #4'
    
    motorY = bedHeight + motorLift
    motor2X = bedWidth + motorTranslate
    
    
    
    def initialize(self):
        
        self.startChains()
        self.drawFrame()
        
        self.setSpindleLocation(self.bedWidth/2,self.bedHeight/2)
        
        self.setInitialZoom()
        
        self.xPosSlider.bind(value=self.xPosSliderValueChange)
        self.yPosSlider.bind(value=self.yPosSliderValueChange)
        
        self.setupSled()
        
        
    def setSpindleLocation(self,x,y):
        
        self.sled.setXY(x,y)
    
    def xPosSliderValueChange(self,callback,value):
        self.setSpindleLocation(value,self.yPosSlider.value)
        
    def yPosSliderValueChange(self,callback,value):
        self.setSpindleLocation(self.xPosSlider.value, value)
    
    def drawFrame(self):
        self.frameLeft.initialize()
        self.frameTop.initialize()
        self.frameRight.initialize()
        self.frameBottom.initialize()
        
        
        self.frameLeft.setStart(0,0)
        self.frameLeft.setEnd(0,self.bedHeight)
        self.frameLeft.color = (1,0,0)
        
        self.frameTop.setStart(0,self.bedHeight)
        self.frameTop.setEnd(self.bedWidth,self.bedHeight)
        self.frameTop.color = (1,0,0)
        
        self.frameRight.setStart(self.bedWidth,0)
        self.frameRight.setEnd(self.bedWidth,self.bedHeight)
        self.frameRight.color = (1,0,0)
        
        self.frameBottom.setStart(0,0)
        self.frameBottom.setEnd(self.bedWidth,0)
        self.frameBottom.color = (1,0,0)
    
    def setupSled(self):
        self.sled.initialize(self.chainA, self.chainB, 1)
    
    def setInitialZoom(self):
        mat = Matrix().scale(.4, .4, 1)
        self.scatterInstance.apply_transform(mat, (0,0))
        
        mat = Matrix().translate(200, 100, 0)
        self.scatterInstance.apply_transform(mat)
    
    def startChains(self):
        self.chainA.initialize()
        self.chainB.initialize()
        self.lineT.initialize()
        self.lineT.color = (0,0,1)
        
        
        self.chainA.setStart(-self.motorTranslate, self.motorY)
        self.chainB.setStart(self.motor2X, self.motorY)
        
        self.lineT.setStart(-self.motorTranslate,self.motorY)
        self.lineT.setEnd(self.motor2X,self.motorY)