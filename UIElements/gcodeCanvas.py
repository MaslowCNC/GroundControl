'''

This module provides a UI element which can display gcode on a Kivy canvas element. It also provides panning 
and zooming features. It was not originally written as a stand alone module which might create some weirdness.

'''

from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line
from DataStructures.makesmithInitFuncs       import MakesmithInitFuncs
from UIElements.positionIndicator            import PositionIndicator
from UIElements.viewMenu                     import ViewMenu
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window

import re
import math

class GcodeCanvas(FloatLayout, MakesmithInitFuncs):
    
    scatterObject     = ObjectProperty(None)
    scatterInstance   = ObjectProperty(None)
    positionIndicator = ObjectProperty(None)
    
    crossPosX = NumericProperty(0)
    crossPosY = NumericProperty(0)
    
    offsetX = NumericProperty(0)
    offsetY = NumericProperty(0)
    lastTouchX = 0
    lastTouchY = 0
    motionFlag = 0
    
    canvasScaleFactor = 1 #scale from mm to pixels
    INCHES            = 25.4
    MILLIMETERS       = 1 
    
    xPosition = 0
    yPosition = 0
    
    def initialzie(self):
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            
            #create the axis lines
            crossLineLength = 10000
            Line(points = (-crossLineLength,0,crossLineLength,0), dash_offset = 5)
            Line(points = (0, -crossLineLength,0,crossLineLength), dash_offset = 5)
            
            #create 4'X8' bounding box
            workspaceHeight    = 1219 #4' in mm
            workspaceWidth     = 2438 #8' in mm
            Line(points = ( -workspaceWidth/2 , -workspaceHeight/2 , workspaceWidth/2 , -workspaceHeight/2), dash_offset = 5)
            Line(points = ( -workspaceWidth/2 , workspaceHeight/2 , workspaceWidth/2 , workspaceHeight/2), dash_offset = 5)
            Line(points = ( -workspaceWidth/2 , -workspaceHeight/2 , -workspaceWidth/2 , workspaceHeight/2), dash_offset = 5)
            Line(points = ( workspaceWidth/2 , -workspaceHeight/2 , workspaceWidth/2 , workspaceHeight/2), dash_offset = 5)
            
            Window.bind(on_resize = self.centerScatter)
            
            Window.bind(on_motion = self.zoom)
            
            self.data.bind(gcode = self.updateGcode)
        
        tempViewMenu = ViewMenu()
        tempViewMenu.setUpData(self.data)
        tempViewMenu.reloadGcode()
    
    def centerScatter(self, *args):
        mat = Matrix().translate(Window.width/2, Window.height/2, 0)
        self.scatterInstance.transform = mat
    
    def zoom(self, callback, type, motion, *args):
        if motion.is_mouse_scrolling:
            scaleFactor = .01
            if motion.button == 'scrollup':
                mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
                self.scatterInstance.apply_transform(mat)
            elif motion.button == 'scrolldown':
                mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
                self.scatterInstance.apply_transform(mat)
    
    def updateGcode(self, *args):
        self.drawgcode()
    
    def setCrossPos(self, xPos, yPos, units):
        '''
        
        Move cross-hairs on UI
        
        '''
        
        if units == "mm":
            self.crossPosX = xPos*self.MILLIMETERS
            self.crossPosY = yPos*self.MILLIMETERS
        elif units == "in":
            self.crossPosX = xPos*self.INCHES
            self.crossPosY = yPos*self.INCHES
        
        
        self.positionIndicator.move(self.crossPosX,self.crossPosY)
    
    def angleGet(self, X, Y, centerX, centerY):
        '''
        
        angleGet returns the angle from the positive x axis to a point given the center of the circle 
        and the point. It is called when plotting circles in the drawGcode() function. Result is returned
        in pi-radians. 
    
        '''
        
        if X == centerX: #this resolves /div0 errors
            #print("special case X")
            if Y >= centerY:
                #print("special case one")
                return(0)
            if Y <= centerY:
                #print("special case two")
                return(1)
        if Y == centerY: #this resolves /div0 errors
            #print("special case Y")
            if X >= centerX:
                #print("special case three")
                return(.5)
            if X <= centerX:
                #print("special case four")
                return(1.5)
        if X > centerX and Y > centerY: #quadrant one
            #print("Quadrant 1")
            theta = math.atan((centerY - Y)/(X - centerX))
            theta = theta/math.pi
            theta = theta + .5
        if X < centerX and Y > centerY: #quadrant two
            #print("Quadrant 2")
            theta = math.atan((Y - centerY)/(X - centerX))
            theta = 1 - theta/math.pi
            theta = theta + .5
        if X < centerX and Y < centerY: #quadrant three
            #print("Quadrant 3")
            theta = math.atan((Y - centerY)/(X - centerX))
            theta = 1 - theta/math.pi
            theta = theta + .5
        if X > centerX and Y < centerY: #quadrant four
            #print("Quadrant 4")
            theta = math.atan((centerY - Y)/(X - centerX))
            theta = theta/math.pi
            theta = theta + .5
        
        return(theta)   
    
    def drawG1(self,gCodeLine):
        
        
        xTarget = self.xPosition
        yTarget = self.yPosition
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])*self.canvasScaleFactor
        
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])*self.canvasScaleFactor
        
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            Line(points = (self.offsetX + self.xPosition , self.offsetY + self.yPosition , self.offsetX +  xTarget, self.offsetY  + yTarget), width = 1, group = 'gcode')
        
        self.xPosition = xTarget
        self.yPosition = yTarget
    
    def drawG2(self,gCodeLine):
        
        xTarget = self.xPosition
        yTarget = self.yPosition
        iTarget = self.xPosition
        jTarget = self.yPosition
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])*self.canvasScaleFactor
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])*self.canvasScaleFactor
        i = re.search("I(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if i:
            iTarget = float(i.groups()[0])*self.canvasScaleFactor
        j = re.search("J(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if j:
            jTarget = float(j.groups()[0])*self.canvasScaleFactor
        
        radius = math.sqrt(iTarget**2 + jTarget**2)
        centerX = self.xPosition + iTarget
        centerY = self.yPosition + jTarget
        
        getAngle1 = self.angleGet(self.xPosition, self.yPosition, centerX, centerY)
        getAngle2 = self.angleGet(xTarget, yTarget, centerX, centerY)
        
        startAngle = math.degrees(math.pi * getAngle1)
        endAngle = math.degrees(math.pi * getAngle2)
        
        if startAngle > endAngle:
            startAngle = startAngle - 360
        
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            Line(circle=(self.offsetX + centerX , self.offsetY + centerY, radius, startAngle, endAngle), group = 'gcode')
        
        
        self.xPosition = xTarget
        self.yPosition = yTarget
    
    def drawG3(self,gCodeLine):
        
        xTarget = self.xPosition
        yTarget = self.yPosition
        iTarget = self.xPosition
        jTarget = self.yPosition
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])*self.canvasScaleFactor
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])*self.canvasScaleFactor
        i = re.search("I(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if i:
            iTarget = float(i.groups()[0])*self.canvasScaleFactor
        j = re.search("J(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if j:
            jTarget = float(j.groups()[0])*self.canvasScaleFactor
        
        radius = math.sqrt(iTarget**2 + jTarget**2)
        centerX = self.xPosition + iTarget
        centerY = self.yPosition + jTarget
        
        getAngle1 = self.angleGet(self.xPosition, self.yPosition, centerX, centerY)
        getAngle2 = self.angleGet(xTarget, yTarget, centerX, centerY)
        
        startAngle = math.degrees(math.pi * getAngle1)
        endAngle = math.degrees(math.pi * getAngle2)
        
        if endAngle > startAngle: #handles case where start and end are across 0 degrees
            endAngle = endAngle - 360
        
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            Line(circle=(self.offsetX + centerX , self.offsetY + centerY, radius, startAngle, endAngle), group = 'gcode')
        
        
        self.xPosition = xTarget
        self.yPosition = yTarget
    
    def clearGcode(self):
        self.scatterObject.canvas.remove_group('gcode')
    
    #This draws the gcode on the canvas.
    def drawgcode(self):
        xnow = 800.0
        ynow = 800.0
        znow = 0
        cutdi = 1
        fillcolor = "green"
        prependString = "G00 "
        
        i = 0
        opstring = ""
        
        self.clearGcode()
        
        if len(self.data.gcode) > 8000:
            errorText = "The current file contains " + str(len(self.data.gcode)) + "lines of gcode.\nrendering all " +  str(len(self.data.gcode)) + " lines simultanously may crash the\n program, only the first 8000 lines are shown here.\nThe complete program will cut if you choose to do so."
            print errorText
            #self.canv.create_text(xnow + 200, ynow - 50, text = errorText, fill = "red")
        
        
        while i < len(self.data.gcode) and i < 8000: #maximum of 8,000 lines are drawn on the screen at a time
            opstring = self.data.gcode[i]
            opstring = opstring + " " #ensures that the is a space at the end of the line
            
            if opstring[0] == 'X' or opstring[0] == 'Y' or opstring[0] == 'Z': #this adds the gcode operator if it is omitted by the program
                opstring = prependString + opstring
            
            if opstring[0:3] == 'G00' or opstring[0:3] == 'G01' or opstring[0:3] == 'G02' or opstring[0:3] == 'G03':
                prependString = opstring[0:3] + " "
            
            if opstring[0:3] == 'G01' or opstring[0:3] == 'G00' or opstring[0:3] == 'G1 ' or opstring[0:3] == 'G0 ':
                self.drawG1(opstring)
                        
            if opstring[0:3] == 'G02' or opstring[0:3] == 'G2 ':
                self.drawG2(opstring)
                               
            if opstring[0:3] == 'G03' or opstring[0:3] == 'G3 ':
                self.drawG3(opstring)
            
            if opstring[0:3] == 'G20':
                self.canvasScaleFactor = self.INCHES
                self.data.gcode_queue.put('G20 ')
                
            if opstring[0:3] == 'G21':
                self.canvasScaleFactor = self.MILLIMETERS
                self.data.gcode_queue.put('G21 ')
                
            if opstring[0:3] == 'G90':
                self.absoluteFlag = 1
                
            if opstring[0:3] == 'G91':
                self.absoluteFlag = 0
            
            if opstring[0] == 'D':
                startpt = opstring.find('D')
                startpt = startpt + 1
                endpt = 0
                j = startpt
                while opstring[j] != ' ':
                    j = j + 1
                endpt = j
                tooldi = float(opstring[startpt : endpt])
                cutdi = scalor*20*tooldi
            
            
            i = i + 1
    