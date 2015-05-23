'''

Kivy Imports

'''
from kivy.app import App
from kivy.properties import OptionProperty, NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics import InstructionGroup
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.popup import Popup

'''

Other Imports

'''

import threading
import Queue
import serial
from time import time
import sys
import re
import math

'''

UI Elements

'''

class GcodeCanvas(FloatLayout):
    crossPosX = NumericProperty(0)
    crossPosY = NumericProperty(0)
    
    offsetX = NumericProperty(300)
    offsetY = NumericProperty(200)
    lastTouchX = 0
    lastTouchY = 0
    
    canvasScaleFactor = 4 #scale from mm to pixels
    
    xPosition = 0
    yPosition = 0
    
    gcode = []
    
    def updateGcode(self):
        self.drawgcode()
    
    def setCrossPos(self, xPos, yPos):
        self.crossPosX = xPos * self.canvasScaleFactor
        self.crossPosY = yPos * self.canvasScaleFactor
    
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
        
        with self.canvas:
            Color(1, 1, 1)
            #print "drawing a line from (" + str(self.xPosition) + "," + str(self.yPosition) + ") to (" + str(xTarget) + "," + str(yTarget) + ")"
            Line(points = (self.offsetX + self.xPosition , self.offsetY + self.yPosition , self.offsetX +  xTarget, self.offsetY  + yTarget), width = 1, group = 'inflections')
        
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
        
        with self.canvas:
            Color(1, 1, 1)
            Line(circle=(self.offsetX + centerX , self.offsetY + centerY, radius, startAngle, endAngle))
            #Line(circle=(self.offsetX + centerX , self.offsetY + centerY, 2))
            #Line(circle=(self.offsetX + self.xPosition , self.offsetY + self.yPosition, 2))
        
        
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
        
        if startAngle == 0:
            startAngle = 360
        
        print "Angles"
        print startAngle
        print endAngle
        
        #startAngle = 360
        #endAngle = 270
        
        with self.canvas:
            Color(1, 1, 1)
            Line(circle=(self.offsetX + centerX , self.offsetY + centerY, radius, endAngle, startAngle))
            #Line(circle=(self.offsetX + centerX , self.offsetY + centerY, 2))
            #Line(circle=(self.offsetX + self.xPosition , self.offsetY + self.yPosition, 2))
        
        
        self.xPosition = xTarget
        self.yPosition = yTarget
    
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
        
        
        
        if len(self.gcode) > 8000:
            errorText = "The current file contains " + str(len(self.gcode)) + "lines of gcode.\nrendering all " +  str(len(self.gcode)) + " lines simultanously may crash the\n program, only the first 8000 lines are shown here.\nThe complete program will cut if you choose to do so."
            print errorText
            #self.canv.create_text(xnow + 200, ynow - 50, text = errorText, fill = "red")
        
        
        while i < len(self.gcode) and i < 8000: #maximum of 8,000 lines are drawn on the screen at a time
            opstring = self.gcode[i]
            opstring = opstring + " " #ensures that the is a space at the end of the line
            
            if opstring[0] == 'X' or opstring[0] == 'Y' or opstring[0] == 'Z': #this adds the gcode operator if it is omited by the program
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
                if self.canvasScaleFactor < 15: #if the machine is currently in mm (this prevents the code from running EVERY time the gcode is redrawn
                    #self.switchinches()
                    pass
                
            if opstring[0:3] == 'G21':
                if self.canvasScaleFactor > 15:
                    pass
                    #self.switchmm()
                
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
    
    def onMotion(self, etype, callback ,motionevent):
        if motionevent.x != 0.0:
            if abs(motionevent.x - self.lastTouchX) > 50:
                self.lastTouchX = motionevent.x
            if abs(motionevent.y - self.lastTouchY) > 50:
                self.lastTouchY = motionevent.y
            
            self.offsetX =  self.offsetX + (motionevent.x - self.lastTouchX)
            self.lastTouchX = motionevent.x
            self.offsetY =  self.offsetY + (motionevent.y - self.lastTouchY)
            self.lastTouchY = motionevent.y
    
class FrontPage(Screen):
    textconsole = ObjectProperty(None)
    connectmenu = ObjectProperty(None) #make ConnectMenu object accessable at this scope
    gcodecanvas = ObjectProperty(None) #make ConnectMenu object accessable at this scope
    
    target = [0,0,0]
    
    distMove = 0
    speedMove = 0
    
    xReadoutPos = StringProperty("0 mm")
    yReadoutPos = StringProperty("0 mm")
    zReadoutPos = StringProperty("0 mm")
    
    stepsizeval = 0
    feedRate = 0
    
    spindleFlag = 0
    
    consoleText = StringProperty(" ")
    
    def setPosReadout(self, xPos, yPos, zPos):
        self.xReadoutPos = str(xPos) + " mm"
        self.yReadoutPos = str(yPos) + " mm"
        self.zReadoutPos = str(zPos) + " mm"
    
    def setupQueues(self, message_queue, gcode_queue, quick_queue):
        self.message_queue = message_queue
        self.gcode_queue = gcode_queue
        self.quick_queue = quick_queue
    
    def jmpsize(self):
        try:
            self.stepsizeval = float(self.moveDistInput.text)
        except:
            pass
        try:
            self.feedRate = float(self.moveSpeedInput.text)
        except:
            pass
    
    def upLeft(self):
        self.jmpsize()
        xtarget = -1*self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)
        
    def upRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def up(self):
        self.jmpsize()
        target = self.target[1] + float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def left(self):
        self.jmpsize()
        target = -1*self.target[0] - float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        
    def right(self):
        self.jmpsize()
        target = -1*self.target[0] + float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        
    def downLeft(self):
        self.jmpsize()
        xtarget = -1*self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)    

    def down(self):
        self.jmpsize()
        target = self.target[1] - float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def downRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def zUp(self):
        self.jmpsize()
        target = self.target[2] + float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] + float(self.stepsizeval)

    def zDown(self):
        self.jmpsize()
        target = self.target[2] - float(self.stepsizeval)
        self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] - float(self.stepsizeval)

    def home(self):
        if self.target[2] < 0:
            self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z0 ")
            self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X0 Y0 Z0 ")
        if self.target[2] >= 0:
            self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X0 Y0 ")
            self.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z0 ")
        self.target[0] = 0.0
        self.target[1] = 0.0
        self.target[2] = 0.0
    
    def stopRun(self):
        #stoprun stops the machine's movement imediatly when it is moving.
        stopflag = 0
        #if self.uploadFlag == 1: 
        #    stopflag = 1
        #self.uploadFlag = 0
        #self.gcodeIndex = 0
        self.quick_queue.put("STOP") 
        with self.gcode_queue.mutex:
            self.gcode_queue.queue.clear()
        print("Gode Stopped")
        
        #self.target[0] = self.dataBack.currentpos[0]/self.dataBack.unitsScale
        #self.target[1] = self.dataBack.currentpos[1]/self.dataBack.unitsScale
        #self.target[2] = self.dataBack.currentpos[2]/self.dataBack.unitsScale
    
    def toggleSpindle(self):
    #toggleSpindle turns on and off the dremel if a relay is attached
        if(self.spindleFlag == 1):
            self.gcode_queue.put("S5000 ")
            self.spindleFlag = 0
        elif(self.dataBack.spindleFlag == 0):
            self.gcode_queue.put("S0 ")
            self.spindleFlag = 1

class OtherFeatures(Screen):
    viewmenu = ObjectProperty(None) #make viewmenu object accessable at this scope

class SoftwareSettings(Screen):
    pass

class ViewMenu(GridLayout):
    gcodeFilePath = ""
    
    def openFile(self):
        '''
        
        Open A File
        
        '''
        self.show_load()
    
    def setGcodeLocation(self,gcodeLocation):
        self.gcodeCanvas = gcodeLocation
        
        #self.gcodeCanvas.gcode = ["G01 X10", "G02 X Y I J"]
        #gcodeLocation.updateGcode()
    
    def show_load(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def load(self, path, filename):
        '''
        from kivy.uix.popup import Popup
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        #locate the file extension
        filename = filename[0]
        fileExtension = filename[-4:]
        
        self.gcodeFilePath = filename
        self.reloadGcode()
        self.dismiss_popup()
    
    def reloadGcode(self):
        #This reloads the gcode from the hard drive in case it has been updated.
        try:
            filename = self.gcodeFilePath
            filterfile = open(filename, 'r')
            rawfilters = filterfile.read()
            filtersparsed = re.split(r'\s(?=G)|\n|\s(?=g)|\s(?=M)', rawfilters) #splits the gcode into elements to be added to the list
            filtersparsed = [x + ' ' for x in filtersparsed] #adds a space to the end of each line
            filtersparsed = [x.lstrip() for x in filtersparsed]
            filtersparsed = [x.replace('X ','X') for x in filtersparsed]
            filtersparsed = [x.replace('Y ','Y') for x in filtersparsed]
            filtersparsed = [x.replace('Z ','Z') for x in filtersparsed]
            filtersparsed = [x.replace('I ','I') for x in filtersparsed]
            filtersparsed = [x.replace('J ','J') for x in filtersparsed]
            filtersparsed = [x.replace('F ','F') for x in filtersparsed]

            self.gcodeCanvas.gcode = filtersparsed
            filterfile.close() #closes the filter save file
        except:
            if filename is not "":
                print "Cannot reopen gcode file. It may have been moved or deleted. To locate it or open a different file use File > Open G-code"
            self.gcodeFilePath = ""
        self.gcodeCanvas.updateGcode()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()

class RunMenu(FloatLayout):
    pass

class ConnectMenu(FloatLayout):
    
    comPorts = []
    comPort = ""
    
    def setupQueues(self, message_queue, gcode_queue, quick_queue):
        self.message_queue = message_queue
        self.gcode_queue = gcode_queue
        self.quick_queue = quick_queue
    
    def reconnect(self, *args):
        print "reconnect pressed"
        self.comPort = '/dev/ttyACM0'
        self.recieveMessage()
    
    def ports(self):
        print "ports"
        self.gcode_queue.put("test gcode");
    
        '''
    
    Serial Connection Functions
    
    '''
    
    def recieveMessage(self):
        #This function opens the thread which handles the input from the serial port
        #It only needs to be run once, it is run by connecting to the machine
        
        print("Starting Second Thread")
        #self.message_queue is the queue which handles passing CAN messages between threads
        x = SerialPort( self.message_queue, self.gcode_queue, self, self.comPort, self.quick_queue)
        self.th=threading.Thread(target=x.getmessage)
        self.th.daemon = True
        self.th.start()
    
    def listSerialPorts(self):
        #Detects all the devices connected to the computer. Returns them as an array.
        import glob
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
            except (ValueError):
                print("Port find error")
        return result
    
    def detectCOMports(self, *args):
        x = []
        
        altPorts = self.listSerialPorts()
        for z in altPorts:
            x.append((z,z))
        
        self.comPorts = x

class SerialPort():
    '''
    
    SerialPort is the thread which handles direct communication with the CNC machine. 
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue 
    queue where they are added to the GUI
    
    '''

    def __init__( self, message_queue, gcode_queue, mainwindow, comport, quick_queue):
        self.message_queue = message_queue
        self.gcode_queue = gcode_queue
        self.quick_queue = quick_queue
        self.mainwindow = mainwindow
        self.comport = comport
        
    def getmessage (self):
        print("Waiting for new message")
        #opens a serial connection called serialCAN
        from time import sleep
        
        try:
            print("connecting")
            serialCAN = serial.Serial(self.comport, 9600, timeout = .25) #self.comport is the com port which is opened
        except:
            print(self.comport + "is unavailable or in use")
            self.message_queue.put("\n" + self.comport + " is unavailable or in use")
        else:
            self.message_queue.put("\r\nConnected on port " + self.comport + "\r\n")
            gcode = ""
            msg = ""
            subReadyFlag = True
            
            serialCAN.parity = serial.PARITY_ODD #This is something you have to do to get the connection to open properly. I have no idea why.
            serialCAN.close()
            serialCAN.open()
            serialCAN.close()
            serialCAN.parity = serial.PARITY_NONE
            serialCAN.open()
            
            print "port open?:"
            print serialCAN.isOpen()
            
            while True:
                
                try:
                    msg = serialCAN.readline() #rand.random()
                except:
                    pass
                try:
                    msg = msg.decode('utf-8')
                except:
                    pass
                    
                if len(msg) > 0:
                    
                    
                    if msg == "gready\r\n":
                        subReadyFlag = True
                        if self.gcode_queue.qsize() >= 1:
                            msg = ""
                    
                    if msg == "Clear Buffer\r\n":
                        print("buffer cleared")
                        while self.gcode_queue.empty() != True:
                            gcode = self.gcode_queue.get_nowait()
                        gcode = ""
                        msg = ""
                    
                    self.message_queue.put(msg)
                    
                msg = ""
                
                if self.gcode_queue.empty() != True and len(gcode) is 0:
                        gcode = self.gcode_queue.get_nowait()
                        gcode = gcode + " "
                if self.quick_queue.empty() != True:
                        qcode = self.quick_queue.get_nowait()
                        qcode = qcode.encode()
                        if qcode == b'Reconnect': #this tells the machine serial thread to close the serial connection
                            qcode = ""
                            print("Attempting to Re-establish connection")
                            serialCAN.close() #closes the serial port
                            sleep(.25)
                            try:
                                serialCAN.open()
                            except:
                                return -1
                        else:
                            try:
                                serialCAN.write(qcode)
                            except:
                                print("write issue 2")
                if len(gcode) > 0 and subReadyFlag is True:
                    gcode = gcode.encode()
                    print("Sending: ")
                    print(gcode)
                    try:
                        serialCAN.write(gcode)
                        gcode = ""  
                    except:
                        print("write issue")
                    subReadyFlag = False
                else:
                    pass

class Diagnostics(FloatLayout):
    pass

class ManualControl(FloatLayout):
    pass

'''

Pop-Up Classes

Classes to define the templates for pop-ups of different types.

'''

class LoadDialog(FloatLayout):
    '''
    
    A Pop-up Dialog To Open A File
    
    '''
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    '''
    
    A Pop-up Dialog To Save A File
    
    '''
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


'''

Data Classes

'''

class Data( ):
    '''

    Data holds a set of variables which are essentially global variables which hold information 
    about the gcode file opened, the machine which is connected, and the user's settings. These 
    variables are NOT thread-safe. The queue system shuld always be used for passing information 
    between threads.

    '''
    def __init__(self):
        #Gcodes contains all of the lines of gcode in the opened file
        self.gcode = []
        self.version = '0.59'
        #all of the available COM ports
        self.comPorts = []
        #A flag to indicate if logging is enabled
        self.logflag = 0
        #A flag to indicate if the main window should auto scroll
        self.scrollFlag = 1
        #The file where logging will take place if it is turned on
        self.logfile = None
        #This defines which COM port is used
        self.comport = "" 
        #The index of the next unread line of Gcode
        self.gcodeIndex = 0
        #The amount to move from one step
        self.stepsizeval = 1
        #Holds the current value of the feed rate
        self.feedRate = 20
        #holds the address of the g-code file so that the gcode can be refreshed
        self.gcodeFile = ""
        #sets a flag if the gcode is being uploaded currently
        self.uploadFlag = 0
        #flag is 1 if the machine is ready for a command
        self.readyFlag = 0
        #the current position of the cutting head
        self.currentpos = [0.0, 0.0, 0.0]
        self.target = [0.0, 0.0, 0.0]
        #click values for drag window
        self.xclickstart = 0
        self.xclickend = 0
        self.yclickstart = 0
        self.yclickend = 0
        self.offsetX = 0
        self.offsetY = 0 #was -200 
        #Zoom level
        self.zoomLevel = 4.9 #4.9 is real size on my monitor
        self.unitsScale = 1/1.27 #this sets the values for inches and mm 
        #Tool Width and Color Flags
        self.toolWidthFlag = 0
        self.colorFlag = 0
        self.spindleFlag = 1
        self.prependString = " "
        self.absoluteFlag = 1
        self.unitsSetFlag = 0 #used once to set the correct units on the machine
        self.startTime = 0
        self.endTime = 0
        self.xDrag = 0
        self.yDrag = 0
        self.saveFlag = 1 #program saves when flag is 1
        self.appData = ""
        self.contrast = 50
        self.backlight = 65
        self.heartBeat = time()
        self.firstTimePosFlag = 0 #this is used to determine the first time the position is recieved from the machine

'''

Main UI Program

'''

class GroundControlApp(App):
    
    def build(self):
        interface = FloatLayout()
        self.dataBack = Data()
        
        #create queues
        message_queue = Queue.Queue()
        gcode_queue = Queue.Queue()
        quick_queue = Queue.Queue()
        
        screenControls = GridLayout(rows = 1, size_hint=(1, .05), pos = (0,Window.height - 50))
        
        btn1 = Button(text='Control', size_hint=(.5, .5))
        btn1.bind(on_press=self.showFront)
        screenControls.add_widget(btn1)
        
        btn2 = Button(text='Other Features', size_hint=(.5, .5))
        btn2.bind(on_press=self.showFeatures)
        screenControls.add_widget(btn2)
        
        
        btn3 = Button(text='Settings', size_hint=(.5, .5))
        btn3.bind(on_press=self.showSettings)
        screenControls.add_widget(btn3)
        
        interface.add_widget(screenControls)
        
        
        self.sm = ScreenManager(transition=SlideTransition(), size_hint=(1, .95), pos = (0,0), clearcolor=(1,1,1,1))
        
        self.frontpage = FrontPage(name='FrontPage')
        self.sm.add_widget(self.frontpage)
        
        self.otherfeatures = OtherFeatures(name='OtherFeatures')
        self.sm.add_widget(self.otherfeatures)
        
        self.softwaresettings = SoftwareSettings(name='SoftwareSettings')
        self.sm.add_widget(self.softwaresettings)
        
        interface.add_widget(self.sm)
        
        self.otherfeatures.connectmenu.setupQueues(message_queue, gcode_queue, quick_queue)
        self.frontpage.setupQueues(message_queue, gcode_queue, quick_queue)
        
        self.otherfeatures.viewmenu.setGcodeLocation(self.frontpage.gcodecanvas)
        
        Clock.schedule_interval(self.otherfeatures.connectmenu.detectCOMports, 2)
        Clock.schedule_interval(self.runPeriodically, .1)
        
        Clock.schedule_once(self.otherfeatures.connectmenu.reconnect, .1)
        
        Window.bind(on_motion = self.frontpage.gcodecanvas.onMotion)
        
        return interface
    
    '''
    
    Update Functions
    
    '''
    
    def runPeriodically(self, *args):
        if not self.otherfeatures.connectmenu.message_queue.empty(): #if there is new data to be read
            message = self.otherfeatures.connectmenu.message_queue.get()
            if message[0:2] == "pz":
                self.setPosOnScreen(message)
            else:
                try:
                    newText = self.frontpage.consoleText[-30:] + message
                    self.frontpage.consoleText = newText
                except:
                    print "text not displayed correctly"
    
    def setPosOnScreen(self, message):
        
 #       try:
        startpt = message.find('(')
        startpt = startpt + 1
        
        endpt = message.find(')')
        
        numz = message[startpt:endpt]
        
        valz = numz.split(",")
        
        xval = -1*float(valz[0])
        yval = float(valz[1])
        zval = float(valz[2])
    
        self.frontpage.setPosReadout(xval,yval,zval)
        self.frontpage.gcodecanvas.setCrossPos(xval,yval)
        
    
    '''

    Show page functions

    '''
    
    def showFront(self, extra):
        self.sm.current = 'FrontPage'
    
    def showFeatures(self, extra):
        self.sm.current = 'OtherFeatures'
    
    def showSettings(self, extra):
        self.sm.current = 'SoftwareSettings'
    
if __name__ == '__main__':
    GroundControlApp().run()
