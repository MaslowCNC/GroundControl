'''

This module provides a UI element which can display gcode on a Kivy canvas element. It also provides panning 
and zooming features. It was not originally written as a stand alone module which might create some weirdness.

'''

from kivy.uix.floatlayout                    import FloatLayout
from kivy.properties                         import NumericProperty, ObjectProperty
from kivy.graphics                           import Color, Ellipse, Line, Point
from kivy.clock                              import Clock
from DataStructures.makesmithInitFuncs       import MakesmithInitFuncs
from UIElements.positionIndicator            import PositionIndicator
from UIElements.viewMenu                     import ViewMenu
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from UIElements.modernMenu                   import ModernMenu
from kivy.metrics                            import dp
from kivy.graphics.texture                   import Texture
from kivy.graphics							 import Rectangle

import re
import math
import global_variables
import sys

class GcodeCanvas(FloatLayout, MakesmithInitFuncs):
    
    canvasScaleFactor = 1 #scale from mm to pixels
    INCHES            = 25.4
    MILLIMETERS       = 1 
    
    xPosition = 0
    yPosition = 0
    zPosition = 0
    
    lineNumber = 0  #the line number currently being processed
    
    absoluteFlag = 0
    
    prependString = "G01 "
    
    maxNumberOfLinesToRead = 300000
    
    
    
    def initialize(self):
        
        self.targetIndicator.color   = self.data.targetInicatorColor
        self.positionIndicator.color = self.data.posIndicatorColor
        
        self.drawWorkspace()

        if self.data.config.getboolean('Ground Control Settings', 'centerCanvasOnResize'):
            Window.bind(on_resize = self.centerCanvas)

        self.data.bind(gcode = self.updateGcode)
        self.data.bind(backgroundRedraw = self.updateGcode)
        self.data.bind(gcodeShift = self.reloadGcode)              #No need to reload if the origin is changed, just clear and redraw
        self.data.bind(gcodeFile = self.centerCanvasAndReloadGcode)
        
        global_variables._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        global_variables._keyboard.bind(on_key_down=self._on_keyboard_down)
        
        self.centerCanvasAndReloadGcode()
    
    def addPoint(self, x, y):
        '''
        
        Add a point to the line currently being plotted
        
        '''

        self.line.points.extend((x,y))
    
    def _keyboard_closed(self):
        '''
        
        If the window looses focus.
        
        '''
        global_variables._keyboard.unbind(on_key_down=self._on_keyboard_down)
        global_variables._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        
        Called when a button is pressed.
        
        '''
        scaleFactor = .03
        anchor = (0,0)
        
        if keycode[1] == self.data.config.get('Ground Control Settings', 'zoomIn'):
            mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
            self.scatterInstance.apply_transform(mat, anchor)
            return True # we handled this key - don't pass to other callbacks
        elif keycode[1] == self.data.config.get('Ground Control Settings', 'zoomOut'):
            mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
            self.scatterInstance.apply_transform(mat, anchor)
            return True # we handled this key - don't pass to other callbacks
        else:
            return False # we didn't handle this key - let next callback handle it

    def isClose(self, a, b):
        return abs(a-b) <= self.data.tolerance

    def centerCanvasAndReloadGcode(self, *args):
        self.centerCanvas()
        self.reloadGcode()
        
    def reloadGcode(self, *args):
        '''
        
        This reloads the gcode from the hard drive in case it has been updated. 
        
        '''
        
        filename = self.data.gcodeFile
        if filename is "": #Blank the g-code if we're loading "nothing"
			self.data.gcode = ""
			return

        try:
            filterfile = open(filename, 'r')
            rawfilters = filterfile.read()

            filtersparsed = re.sub(r'\(([^)]*)\)','\n',rawfilters) #replace mach3 style gcode comments with newline
            filtersparsed = re.sub(r';([^\n]*)\n','\n',filtersparsed) #replace standard ; initiated gcode comments with newline
            filtersparsed = re.sub(r'\n\n','\n',filtersparsed) #removes blank lines
            filtersparsed = re.sub(r'([0-9])([GXYZIJFTM]) *', '\\1 \\2',filtersparsed) #put spaces between gcodes
            filtersparsed = re.sub(r'  +',' ',filtersparsed) #condense space runs

            if self.data.config.getint('Advanced Settings','truncate'):
                digits = self.data.config.get('Advanced Settings','digits')
                filtersparsed = re.sub(r'([+-]?\d*\.\d{1,'+digits+'})(\d*)',r'\g<1>',filtersparsed) #truncates all long floats to 4 decimal places, leaves shorter floats

            filtersparsed = re.split('\n', filtersparsed) #splits the gcode into elements to be added to the list
            filtersparsed = [x + ' ' for x in filtersparsed] #adds a space to the end of each line
            filtersparsed = [x.lstrip() for x in filtersparsed]
            filtersparsed = [x.replace('X ','X') for x in filtersparsed]
            filtersparsed = [x.replace('Y ','Y') for x in filtersparsed]
            filtersparsed = [x.replace('Z ','Z') for x in filtersparsed]
            filtersparsed = [x.replace('I ','I') for x in filtersparsed]
            filtersparsed = [x.replace('J ','J') for x in filtersparsed]
            filtersparsed = [x.replace('F ','F') for x in filtersparsed]
            
            self.data.gcode = "[]"
            self.data.gcode = filtersparsed
            
            filterfile.close() #closes the filter save file

            #Find gcode indicies of z moves
            self.data.zMoves = [0]
            zList = []
            for index, line in enumerate(self.data.gcode):
                z = re.search("Z(?=.)([+-]?([0-9]*)(\.([0-9]+))?)",line)
                if z:
                    zList.append(z)
                    if len(zList) > 1:
                        if not self.isClose(float(zList[-1].groups()[0]),float(zList[-2].groups()[0])):
                            self.data.zMoves.append(index-1)
                    else:
                        self.data.zMoves.append(index)
        except:
            self.data.message_queue.put("Message: Cannot reopen gcode file. It may have been moved or deleted. To locate it or open a different file use Actions > Open G-code")
            self.data.gcodeFile = ""
    
    def centerCanvas(self, *args):
        '''
        
        Return the canvas to the center of the screen.
        
        '''
        mat = Matrix().translate(Window.width/2, Window.height/2, 0)
        self.scatterInstance.transform = mat
        
        anchor = (0,0)
        scale = self.data.config.get('Ground Control Settings', 'viewScale')
        mat = Matrix().scale(dp(scale), dp(scale), 1)

        self.scatterInstance.apply_transform(mat, anchor)

    def on_touch_up(self, touch, *args):
        
        if touch.is_mouse_scrolling:
            self.zoomCanvas(touch)
        
        return super(GcodeCanvas, self).on_touch_up(touch, *args)
    
    def zoomCanvas(self, touch):
        if touch.is_mouse_scrolling:
            scaleFactor = .1
            
            if touch.button == 'scrollup':
                mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor = touch.pos)
            elif touch.button == 'scrolldown':
                mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
                self.scatterInstance.apply_transform(mat, anchor = touch.pos)

    def drawWorkspace(self, *args):

        self.scatterObject.canvas.remove_group('workspace')
 
        with self.scatterObject.canvas:
            Color(.47, .47, .47)

            #create the bounding box
            height = float(self.data.config.get('Maslow Settings', 'bedHeight'))
            width  = float(self.data.config.get('Maslow Settings', 'bedWidth'))
            Line(points = ( -width/2 , -height/2 ,  width/2 , -height/2), group='workspace')
            Line(points = ( -width/2 ,  height/2 ,  width/2 ,  height/2), group='workspace')
            Line(points = ( -width/2 , -height/2 , -width/2 ,  height/2), group='workspace')
            Line(points = (  width/2 , -height/2 ,  width/2 ,  height/2), group='workspace')
            
            #create the axis lines
            Line(points = (-width/2,0,width/2,0), dash_offset = 5, group='workspace')
            Line(points = (0, -height/2,0,height/2), dash_offset = 5, group='workspace')
    
            texture = self.data.backgroundTexture
            if texture is not None:
                Rectangle(texture=texture, pos=(-width/2, -height/2), 
                          size=(width, height),
                          tex_coords=self.data.backgroundManualReg)

    def drawLine(self,gCodeLine,command):
        '''
        
        drawLine draws a line using the previous command as the start point and the xy coordinates
        from the current command as the end point. The line is styled based on the command to allow
        visually differentiating between normal and rapid moves. If the z-axis depth is changed a
        circle is placed at the location of the depth change to alert the user. 
    
        '''
        
        try:
            xTarget = self.xPosition
            yTarget = self.yPosition
            zTarget = self.zPosition
            
            x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0])*self.canvasScaleFactor
                if self.absoluteFlag == 1:
                    xTarget = self.xPosition + xTarget
            
            y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
                yTarget = float(y.groups()[0])*self.canvasScaleFactor
                if self.absoluteFlag == 1:
                    yTarget = self.yPosition + yTarget
            z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if z:
                zTarget = float(z.groups()[0])*self.canvasScaleFactor
            
            
            #Draw lines for G1 and G0
            with self.scatterObject.canvas:
                Color(self.data.drawingColor[0], self.data.drawingColor[1], self.data.drawingColor[2])
                
                if command == 'G00':
                    #draw a dashed line
                    Line(points = (self.xPosition , self.yPosition , xTarget, yTarget), width = 1, group = 'gcode', dash_length = 4, dash_offset = 2)
                    
                    #start a new straight line from the end of the dashed line
                    self.line = Line(points = (), width = 1, group = 'gcode')
                    self.addPoint(xTarget , yTarget)
                else:
                    self.addPoint(xTarget , yTarget)
                
            #If the zposition has changed, add indicators
            tol = 0.05 #Acceptable error in mm
            if abs(zTarget - self.zPosition) >= tol:
                with self.scatterObject.canvas:
                    if zTarget - self.zPosition > 0:
                        Color(0, 1, 0)
                        radius = 1
                    else:
                        Color(1, 0, 0)
                        radius = 2
                    Line(circle=(self.xPosition , self.yPosition, radius), group = 'gcode')
                    Color(self.data.drawingColor[0], self.data.drawingColor[1], self.data.drawingColor[2])
            
            self.xPosition = xTarget
            self.yPosition = yTarget
            self.zPosition = zTarget
        except:
            print "Unable to draw line on screen: " + gCodeLine
    
    def drawArc(self,gCodeLine,command):
        '''
        
        drawArc draws an arc using the previous command as the start point, the xy coordinates from
        the current command as the end point, and the ij coordinates from the current command as the
        circle center. Clockwise or counter-clockwise travel is based on the command. 
    
        '''
        
        try:
            xTarget = self.xPosition
            yTarget = self.yPosition
            iTarget = 0
            jTarget = 0
            
            x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0])*self.canvasScaleFactor
            y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
                yTarget = float(y.groups()[0])*self.canvasScaleFactor
            i = re.search("I(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if i:
                iTarget = float(i.groups()[0])*self.canvasScaleFactor
            j = re.search("J(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if j:
                jTarget = float(j.groups()[0])*self.canvasScaleFactor
            
            radius = math.sqrt(iTarget**2 + jTarget**2)
            centerX = self.xPosition + iTarget
            centerY = self.yPosition + jTarget
            
            angle1 = math.atan2(self.yPosition - centerY, self.xPosition - centerX)
            angle2 = math.atan2(yTarget - centerY, xTarget - centerX)
            
            
            #atan2 returns results from -pi to +pi and we want results from 0 - 2pi
            if angle1 < 0:
                angle1 = angle1 + 2*math.pi
            if angle2 < 0:
                angle2 = angle2 + 2*math.pi
            
            
            #take into account command G1 or G2
            if int(command[1:]) == 2:
                if angle1 < angle2:
                    angle1 = angle1 + 2*math.pi
                direction = -1
            else:
                if angle2 < angle1:
                    angle2 = angle2 + 2*math.pi
                direction = 1
            
            arcLen = abs(angle1 - angle2)
            if abs(angle1 - angle2) == 0:
                arcLen = 6.28313530718
            
            i = 0
            while abs(i) < arcLen:
                xPosOnLine = centerX + radius*math.cos(angle1 + i)
                yPosOnLine = centerY + radius*math.sin(angle1 + i)
                self.addPoint(xPosOnLine , yPosOnLine)
                i = i+.1*direction #this is going to need to be a direction 
            
            self.addPoint(xTarget , yTarget)
            
            self.xPosition = xTarget
            self.yPosition = yTarget
        except:
            print "Unable to draw arc on screen: " + gCodeLine

    def clearGcode(self):
        '''
        
        clearGcode deletes the lines and arcs corresponding to gcode commands from the canvas. 
    
        '''
        self.scatterObject.canvas.clear()#remove_group('gcode')
        
        self.drawWorkspace()
    
    def moveToPos(self, xPosition, yPosition, *args):
        '''
        
        Move the machine to a point selected on the screen
        
        '''
        
        if self.data.units == 'MM':
            scaleFactor = 1
        else:
            scaleFactor = 25.4
        
        xTarget = '%.3f'%(xPosition/scaleFactor)
        yTarget = '%.3f'%(yPosition/scaleFactor)
        commandString = 'G0 X' + str(xTarget) + ' Y' + str(yTarget) + " "
        
        self.data.gcode_queue.put(commandString)
    
    def createMark(self, xPosition, yPosition, *args):
        '''
        
        Create a mark at a point selected on the screen
        
        '''
        
        if self.data.units == 'MM':
            scaleFactor = 1
        else:
            scaleFactor = 25.4
        
        xTarget = xPosition/scaleFactor
        yTarget = yPosition/scaleFactor
        marker = PositionIndicator()
        marker.setPos(xTarget, yTarget, self.data.units)
        marker.color = (0,1,0)
        self.scatterInstance.add_widget(marker)
    
    def setHome(self, xPosition, yPosition, *args):
        '''
        
        Set the home position to the location set in the long press menu
        
        '''
        
        if self.data.units == 'MM':
            scaleFactor = 1
        else:
            scaleFactor = 25.4
        
        xPosition = xPosition/scaleFactor
        yPosition = yPosition/scaleFactor
        
        self.data.gcodeShift = [xPosition,yPosition]
        self.data.config.set('Advanced Settings', 'homeX', str(xPosition))
        self.data.config.set('Advanced Settings', 'homeY', str(yPosition))
    
    def doNothing(self, *args):
        '''
        
        A placeholder function which does nothing
        
        '''
        pass
    
    def moveLine(self, gCodeLine):
        
        originalLine = gCodeLine
        
        try:
            gCodeLine = gCodeLine.upper() + " "
            x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
#                 xTarget = '%f' % (float(x.groups()[0]) + self.data.gcodeShift[0]) # not used any more...
                eNtnX = re.sub('\-?\d\.|\d*e-','',str(abs(float(x.groups()[0]) + self.data.gcodeShift[0]))) # strip off everything but the decimal part or e-notation exponent
                e = re.search(".*e-", str(abs(float(x.groups()[0]) + self.data.gcodeShift[0])))
                if e:
                    fmtX = "%0%.%sf" % eNtnX  # if e-notation, use the exponent from the e notation
                else:
                    fmtX = "%0%.%sf" % len(eNtnX) # use the number of digits after the decimal place
                gCodeLine = gCodeLine[0:x.start()+1] + (fmtX % (float(x.groups()[0]) + self.data.gcodeShift[0])) + gCodeLine[x.end():]
            
            y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
#                 yTarget = '%f' % (float(y.groups()[0]) + self.data.gcodeShift[1]) # not used any more...
                eNtnY = re.sub('\-?\d\.|\d*e-','',str(abs(float(y.groups()[0]) + self.data.gcodeShift[1])))
                e = re.search(".*e-", str(abs(float(y.groups()[0]) + self.data.gcodeShift[1])))
                if e:
                    fmtY = "%0%.%sf" % eNtnY
                else:
                    fmtY = "%0%.%sf" % len(eNtnY)
                gCodeLine = gCodeLine[0:y.start()+1] + (fmtY % (float(y.groups()[0]) + self.data.gcodeShift[1])) + gCodeLine[y.end():]
            
            return gCodeLine
        except ValueError:
            print "line could not be moved:"
            print originalLine
            return originalLine
    
    def loadNextLine(self):
        '''
        
        Load the next line of gcode
        
        '''
        
        try:
            self.data.gcode[self.lineNumber] = self.moveLine(self.data.gcode[self.lineNumber])    #move the line if the gcode has been moved
            fullString = self.data.gcode[self.lineNumber]
            self.lineNumber = self.lineNumber + 1
        except:
            return #we have reached the end of the file
        
        #if the line contains multiple gcode commands split them and execute them individually
        listOfLines = fullString.split('G')
        
        if len(listOfLines) > 1:                              #if the line contains at least one 'G'
            for line in listOfLines:
                if len(line) > 0:                                   #If the line is not blank
                    self.updateOneLine('G' + line)                     #Draw it
        else:
            self.updateOneLine(fullString)
        
    def updateOneLine(self, fullString):
        '''
        
        Draw the next line on the gcode canvas
        
        '''
        
        validPrefixList = ['G00','G0 ','G1 ','G01','G2 ','G02','G3 ','G03', 'G17']
        
        fullString = fullString + " " #ensures that there is a space at the end of the line
        
        #find 'G' anywhere in string
        gString = fullString[fullString.find('G'):fullString.find('G') + 3]
        
        if gString in validPrefixList:
            self.prependString = gString
        
        if fullString.find('G') == -1: #this adds the gcode operator if it is omitted by the program
            fullString = self.prependString + ' ' + fullString
            gString = self.prependString
        
        if gString == 'G00' or gString == 'G0 ':
            self.drawLine(fullString, 'G00')

        if gString == 'G01' or gString == 'G1 ':
            self.drawLine(fullString, 'G01')
                    
        if gString == 'G02' or gString == 'G2 ':
            self.drawArc(fullString, 'G02')
                           
        if gString == 'G03' or gString == 'G3 ':
            self.drawArc(fullString, 'G03')
        
        if gString == 'G17':
            #Take no action, XY coordinate plane is the default
            pass
        
        if gString == 'G18':
            print "G18 not supported"
        
        if gString == 'G20':
            self.canvasScaleFactor = self.INCHES
            self.data.units = "INCHES"
            
        if gString == 'G21':
            self.canvasScaleFactor = self.MILLIMETERS
            self.data.units = "MM"
        
        if gString == 'G90':
            self.absoluteFlag = 0
            
        if gString == 'G91':
            self.absoluteFlag = 1
        
    def callBackMechanism(self, callback) :
        '''
        
        Call the loadNextLine function periodically in a non-blocking way to
        update the gcode.
        
        '''
        
        with self.scatterObject.canvas:
            self.line = Line(points = (), width = 1, group = 'gcode')
        
        #Draw numberOfTimesToCall lines on the canvas
        numberOfTimesToCall = 500
        for _ in range(numberOfTimesToCall):
            self.loadNextLine()
        
        #Repeat until end of file
        if self.lineNumber < min(len(self.data.gcode),self.maxNumberOfLinesToRead):
            Clock.schedule_once(self.callBackMechanism)
    
    def updateGcode(self, *args):
        '''
        
        updateGcode parses the gcode commands and calls the appropriate drawing function for the 
        specified command. 
    
        '''
        
        #reset variables 
        self.data.backgroundRedraw = False
        self.xPosition = self.data.gcodeShift[0]*self.canvasScaleFactor
        self.yPosition = self.data.gcodeShift[1]*self.canvasScaleFactor
        self.zPosition = 0

        self.prependString = "G00 "
        self.lineNumber = 0
        
        self.clearGcode()
        
        #Check to see if file is too large to load
        if len(self.data.gcode) > self.maxNumberOfLinesToRead:
            errorText = "The current file contains " + str(len(self.data.gcode)) + " lines of gcode.\nrendering all " +  str(len(self.data.gcode)) + " lines simultaneously may crash the\n program, only the first " + self.maxNumberOfLinesToRead + "lines are shown here.\nThe complete program will cut if you choose to do so unless the home position is moved from (0,0)."
            print errorText
            self.data.message_queue.put("Message: " + errorText)
        
        self.callBackMechanism(self.updateGcode)
        
