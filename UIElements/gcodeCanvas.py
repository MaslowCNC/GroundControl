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
    
    offsetX = NumericProperty(0)
    offsetY = NumericProperty(0)
    
    canvasScaleFactor = 1 #scale from mm to pixels
    INCHES            = 25.4
    MILLIMETERS       = 1 
    
    xPosition = 0
    yPosition = 0
    zPosition = 0
    
    def initialize(self):

        self.drawWorkspace()
            
        Window.bind(on_resize = self.centerScatter)
        Window.bind(on_motion = self.zoom)

        self.data.bind(gcode = self.updateGcode)

        tempViewMenu = ViewMenu()
        tempViewMenu.setUpData(self.data)
        tempViewMenu.reloadGcode()
    
    def centerCanvas(self, *args):
        mat = Matrix().translate(Window.width/2, Window.height/2, 0)
        self.scatterInstance.transform = mat
    
    def zoomCanvas(self, callback, type, motion, *args):
        if motion.is_mouse_scrolling:
            scaleFactor = .03
            
            anchor = (0,0)
            
            if motion.button == 'scrollup':
                mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor)
            elif motion.button == 'scrolldown':
                mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor)

    def drawWorkspace(self, *args):

        self.scatterObject.canvas.remove_group('workspace')
 
        with self.scatterObject.canvas:
            Color(1, 1, 1)

            #create the bounding box
            height = float(self.data.config.get('Maslow Settings', 'bedHeight'))
            width  = float(self.data.config.get('Maslow Settings', 'bedWidth'))
            Line(points = ( -width/2 , -height/2 ,  width/2 , -height/2), dash_offset = 5, group='workspace')
            Line(points = ( -width/2 ,  height/2 ,  width/2 ,  height/2), dash_offset = 5, group='workspace')
            Line(points = ( -width/2 , -height/2 , -width/2 ,  height/2), dash_offset = 5, group='workspace')
            Line(points = (  width/2 , -height/2 ,  width/2 ,  height/2), dash_offset = 5, group='workspace')
            
            #create the axis lines
            Line(points = (-width/2,0,width/2,0), dash_offset = 5, group='workspace')
            Line(points = (0, -height/2,0,height/2), dash_offset = 5, group='workspace')

    def calcAngle(self, X, Y, centerX, centerY):
        '''
        
        calcAngle returns the angle from the positive x axis to a point given the center of the circle 
        and the point. Angle returned in degrees.
    
        '''

        #Special cases at quadrant boundaries (resolves /div0 errors)
        if X == centerX:
            if Y >= centerY: theta = -0.5*math.pi
            if Y < centerY:  theta = 0.5*math.pi
        elif Y == centerY:
            if X > centerX: theta = 0.0*math.pi
            if X < centerX: theta = 1.0*math.pi

        #Normal cases
        if X > centerX and Y > centerY: #quadrant one
            theta = math.atan((centerY - Y)/(X - centerX))
        if X < centerX and Y > centerY: #quadrant two
            theta = math.atan((Y - centerY)/(X - centerX))
            theta = 1.0*math.pi - theta
        if X < centerX and Y < centerY: #quadrant three
            theta = math.atan((Y - centerY)/(X - centerX))
            theta = 1.0*math.pi - theta
        if X > centerX and Y < centerY: #quadrant four
            theta = math.atan((centerY - Y)/(X - centerX))
        
        return(math.degrees(theta + 0.5*math.pi))   
    
    def drawLine(self,gCodeLine,command):
        '''
        
        drawLine draws a line using the previous command as the start point and the xy coordinates
        from the current command as the end point. The line is styled based on the command to allow
        visually differentiating between normal and rapid moves. If the z-axis depth is changed a
        circle is placed at the location of the depth change to alert the user. 
    
        '''
        
        xTarget = self.xPosition
        yTarget = self.yPosition
        zTarget = self.zPosition
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])*self.canvasScaleFactor
        
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])*self.canvasScaleFactor
        
        z = re.search("Z(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if z:
            zTarget = float(z.groups()[0])*self.canvasScaleFactor
        
        
        #Draw lines for G1 and G0
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            if command == 'G00':
                Line(points = (self.offsetX + self.xPosition , self.offsetY + self.yPosition , self.offsetX +  xTarget, self.offsetY  + yTarget), width = 1, group = 'gcode', dash_length = 4, dash_offset = 2)
            elif command == 'G01':
                Line(points = (self.offsetX + self.xPosition , self.offsetY + self.yPosition , self.offsetX +  xTarget, self.offsetY  + yTarget), width = 1, group = 'gcode')
       
        #If the zposition has changed, add indicators
        tol = 0.05 #Acceptable error in mm
        if abs(zTarget - self.zPosition) >= tol:
            with self.scatterObject.canvas:
                if zTarget - self.zPosition > 0:
                    Color(0, 1, 0)
                    radius = 2
                else:
                    Color(1, 0, 0)
                    radius = 4
                Line(circle=(self.offsetX + self.xPosition , self.offsetY + self.yPosition, radius), width = 2, group = 'gcode')
        
        self.xPosition = xTarget
        self.yPosition = yTarget
        self.zPosition = zTarget
    
    def drawArc(self,gCodeLine,command):
        '''
        
        drawArc draws an arc using the previous command as the start point, the xy coordinates from
        the current command as the end point, and the ij coordinates from the current command as the
        circle center. Clockwise or counter-clockwise travel is based on the command. 
    
        '''
        
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
        
        angle1 = self.calcAngle(self.xPosition, self.yPosition, centerX, centerY)
        angle2 = self.calcAngle(xTarget, yTarget, centerX, centerY)
        
        if command == 'G02':
            angleStart = angle2
            angleEnd = angle1
        elif command == 'G03':
            angleStart = angle1
            angleEnd = angle2
        
        if angleStart < angleEnd:
            angleEnd = angleEnd - 360
        
        #Draw arc for G02 and G03
        with self.scatterObject.canvas:
            Color(1, 1, 1)
            Line(circle=(self.offsetX + centerX , self.offsetY + centerY, radius, angleStart, angleEnd), group = 'gcode')

        self.xPosition = xTarget
        self.yPosition = yTarget

    def clearGcode(self):
        '''
        
        clearGcode deletes the lines and arcs corresponding to gcode commands from the canvas. 
    
        '''
        self.scatterObject.canvas.remove_group('gcode')

    def updateGcode(self, *args):
        '''
        
        updateGcode parses the gcode commands and calls the appropriate drawing function for the 
        specified command. 
    
        '''
        self.xPosition = 0
        self.yPosition = 0
        self.zPosition = 0

        prependString = "G00 "
        
        opstring = ""
        
        self.clearGcode()
        
        if len(self.data.gcode) > 8000:
            errorText = "The current file contains " + str(len(self.data.gcode)) + "lines of gcode.\nrendering all " +  str(len(self.data.gcode)) + " lines simultanously may crash the\n program, only the first 8000 lines are shown here.\nThe complete program will cut if you choose to do so."
            print errorText
            #self.canv.create_text(xnow + 200, ynow - 50, text = errorText, fill = "red")

        for i in range(0, min(len(self.data.gcode),8000)): #maximum of 8,000 lines are drawn on the screen at a time
            opstring = self.data.gcode[i]
            opstring = opstring + " " #ensures that the is a space at the end of the line
            
            if opstring[0] == 'X' or opstring[0] == 'Y' or opstring[0] == 'Z': #this adds the gcode operator if it is omitted by the program
                opstring = prependString + opstring
            
            if opstring[0:3] == 'G00' or opstring[0:3] == 'G01' or opstring[0:3] == 'G02' or opstring[0:3] == 'G03':
                prependString = opstring[0:3] + " "
            
            if opstring[0:3] == 'G00' or opstring[0:3] == 'G0 ':
                self.drawLine(opstring, 'G00')

            if opstring[0:3] == 'G01' or opstring[0:3] == 'G1 ':
                self.drawLine(opstring, 'G01')
                        
            if opstring[0:3] == 'G02' or opstring[0:3] == 'G2 ':
                self.drawArc(opstring, 'G02')
                               
            if opstring[0:3] == 'G03' or opstring[0:3] == 'G3 ':
                self.drawArc(opstring, 'G03')
            
            if opstring[0:3] == 'G20':
                self.canvasScaleFactor = self.INCHES
                self.data.units = "INCHES"
                
            if opstring[0:3] == 'G21':
                self.canvasScaleFactor = self.MILLIMETERS
                self.data.units = "MM"
                
            if opstring[0:3] == 'G90':
                self.absoluteFlag = 1
                
            if opstring[0:3] == 'G91':
                self.absoluteFlag = 0
            
            if opstring[0] == 'D':
                pass
    