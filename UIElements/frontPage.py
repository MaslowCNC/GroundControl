'''

This module defines the appearance and function of the front page of the program.

This page is used to manually move the machine, see the positional readout, and view the file being cut

'''

from kivy.uix.screenmanager                    import Screen
from kivy.properties                           import ObjectProperty, StringProperty
from DataStructures.makesmithInitFuncs         import MakesmithInitFuncs
from kivy.uix.popup                            import Popup
from UIElements.touchNumberInput               import TouchNumberInput
import re

class FrontPage(Screen, MakesmithInitFuncs):
    textconsole    = ObjectProperty(None)
    connectmenu    = ObjectProperty(None) #make ConnectMenu object accessible at this scope
    gcodecanvas    = ObjectProperty(None) 
    screenControls = ObjectProperty(None) 
    
    target = [0,0,0]
    
    connectionStatus = StringProperty("Not Connected")
    
    xReadoutPos = StringProperty("0 mm")
    yReadoutPos = StringProperty("0 mm")
    zReadoutPos = StringProperty("0 mm")
    
    percentComplete = StringProperty("0.0%")
    
    numericalPosX  = 0.0
    numericalPosY  = 0.0
    
    stepsizeval = 0
    feedRate = 0
    
    shiftX = 0
    shiftY = 0
    
    consoleText = StringProperty(" ")
    
    units = StringProperty("MM")
    gcodeLineNumber = StringProperty('0')
    
    firstPosFlag = 1
    
    
    def __init__(self, data, **kwargs):
        super(FrontPage, self).__init__(**kwargs)
        self.data = data
    
    def setPosReadout(self, xPos, yPos, zPos, units):
        self.xReadoutPos    = str(xPos) + " " + units
        self.yReadoutPos    = str(yPos) + " " + units
        self.zReadoutPos    = str(zPos) + " " + units
        self.numericalPosX  = xPos
        self.numericalPosY  = yPos
        
        if self.firstPosFlag == True:
            self.target[0] = xPos
            self.target[1] = yPos
            self.target[2] = zPos
            self.firstPosFlag = False
    
    def setUpData(self, data):
        self.gcodecanvas.setUpData(data)
        self.screenControls.setUpData(data)
        self.data.bind(connectionStatus = self.updateConnectionStatus)
        self.data.bind(units            = self.onUnitsSwitch)
        self.data.bind(gcodeIndex       = self.onIndexMove)
        self.data.bind(gcodeFile        = self.onGcodeFileChange)
    
    def updateConnectionStatus(self, callback, connected):
        
        if connected:
            self.connectionStatus = "Connected"
        else:
            self.connectionStatus = "Connection Lost"
    
    def switchUnits(self):
        if self.data.units == "INCHES":
            self.data.units = "MM"
        else:
            self.data.units = "INCHES"
    
    def onUnitsSwitch(self, callback, newUnits):
        self.units = newUnits
        INCHESTOMM  =    1/25.4
        MMTOINCHES  =    25.4
        #the behavior of notifying the machine doesn't really belong here
        #but I'm not really sure where else it does belong
        if newUnits == "INCHES":
            self.data.gcode_queue.put('G20 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)/25)
            self.target[0] = self.target[0]*INCHESTOMM
            self.target[1] = self.target[1]*INCHESTOMM
            self.target[2] = self.target[2]*INCHESTOMM
        else:
            self.data.gcode_queue.put('G21 ')
            self.moveDistInput.text = str(float(self.moveDistInput.text)*25)
            self.target[0] = self.target[0]*MMTOINCHES
            self.target[1] = self.target[1]*MMTOINCHES
            self.target[2] = self.target[2]*MMTOINCHES
    
    def onIndexMove(self, callback, newIndex):
        self.gcodeLineNumber = str(newIndex)
        self.percentComplete = '%.1f' %(100* (float(newIndex) / len(self.data.gcode))) + "%"
    
    def onGcodeFileChange(self, callback, newGcode):
    
        #reset the shift values to 0 because the new gcode is not loaded with a shift applied
        self.shiftX = 0
        self.shiftY = 0
    
    def moveGcodeIndex(self, dist):
        maxIndex = len(self.data.gcode)-1
        targetIndex = self.data.gcodeIndex + dist

        if targetIndex < 0:
            self.data.gcodeIndex = 0
        elif targetIndex > maxIndex:
            self.data.gcodeIndex = maxIndex
        else:
            self.data.gcodeIndex = targetIndex

        gCodeLine = self.data.gcode[self.data.gcodeIndex]
        
        xTarget = 0
        yTarget = 0
        
        x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if x:
            xTarget = float(x.groups()[0])
        else:
            if self.data.units == "INCHES":
                xTarget = self.gcodecanvas.positionIndicator.pos[0] / 25.4
            else:
                xTarget = self.gcodecanvas.positionIndicator.pos[0]              
        
        y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
        if y:
            yTarget = float(y.groups()[0])
        else:
            if self.data.units == "INCHES":
                yTarget = self.gcodecanvas.positionIndicator.pos[1] / 25.4
            else:
                yTarget = self.gcodecanvas.positionIndicator.pos[1] 
        
        self.gcodecanvas.positionIndicator.setPos(xTarget,yTarget,self.data.units, 0)
    
    def pause(self):
        self.data.uploadFlag = 0
        self.data.quick_queue.put("STOP") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        print("Run Paused")
    
    def jmpsize(self):
        try:
            self.stepsizeval = float(self.moveDistInput.text)
        except:
            pass
        try:
            self.feedRate = float(self.moveSpeedInput.text)
        except:
            pass
    
    def test(self):
        print "test has no current function"
    
    def upLeft(self):
        self.jmpsize()
        xtarget = self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget
        
    def upRight(self):
        self.jmpsize()
        xtarget = self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def up(self):
        self.jmpsize()
        target = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = target

    def left(self):
        self.jmpsize()
        target = self.target[0] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = target
        
    def right(self):
        self.jmpsize()
        target = self.target[0] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = target
        
    def downLeft(self):
        self.jmpsize()
        xtarget = self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def down(self):
        self.jmpsize()
        target = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = target

    def downRight(self):
        self.jmpsize()
        xtarget = self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def zUp(self):
        self.jmpsize()
        target = self.target[2] + 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] + 0.10*float(self.stepsizeval)

    def zDown(self):
        self.jmpsize()
        target = self.target[2] - 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] - 0.10*float(self.stepsizeval)

    def zeroZ(self):
        self.data.gcode_queue.put("G10 Z0 ")
        self.target[2] = 0
        
    def home(self):
        if self.target[2] < 0:
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z0 ")
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(self.shiftX) + " Y" + str(self.shiftY) + " ")
        if self.target[2] >= 0:
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " X" + str(self.shiftX) + " Y" + str(self.shiftY) + " ")
            self.data.gcode_queue.put("G00 F" + str(float(self.feedRate)) + " Z0 ")
        self.target[0] = self.shiftX
        self.target[1] = self.shiftY
        self.target[2] = 0.0
    
    def moveLine(self, gcodeLine, moveXBy, moveYBy):
        
        originalLine = gcodeLine
        
        try:
            gcodeLine = gcodeLine.upper() + " "
            
            
            x = gcodeLine.find('X')
            if x != -1:
                space = gcodeLine.find(' ', x)
                number = float(gcodeLine[x+1:space]) + moveXBy
                gcodeLine = gcodeLine[0:x+1] + str(number) + gcodeLine[space:]
            
            y = gcodeLine.find('Y')
            if y != -1:
                space = gcodeLine.find(' ', y)
                number = float(gcodeLine[y+1:space]) + moveYBy
                gcodeLine = gcodeLine[0:y+1] + str(number) + gcodeLine[space:]
            
            return gcodeLine
        except ValueError:
            print "line could not be moved:"
            print originalLine
            return originalLine
    
    def moveOrigin(self):
        
        if self.data.units == "INCHES":
            amtToShiftX = self.numericalPosX - self.shiftX
            amtToShiftY = self.numericalPosY - self.shiftY
            self.shiftX = self.shiftX + amtToShiftX
            self.shiftY = self.shiftY + amtToShiftY
        else:
            amtToShiftX = self.numericalPosX - self.shiftX
            amtToShiftY = self.numericalPosY - self.shiftY
            self.shiftX = self.shiftX + amtToShiftX
            self.shiftY = self.shiftY + amtToShiftY
        
        shiftedGcode = []
        
        for line in self.data.gcode:
            shiftedGcode.append(self.moveLine(line , amtToShiftX, amtToShiftY))
        
        self.data.gcode = shiftedGcode
    
    def startRun(self):
        
        self.data.uploadFlag = 1
        self.sendLine()
    
    def sendLine(self):
        try:
            self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
            self.data.gcodeIndex = self.data.gcodeIndex + 1
        except:
            print "gcode run complete"
            self.gcodecanvas.uploadFlag = 0
            self.data.gcodeIndex = 0
    
    def stopRun(self):
        self.data.uploadFlag = 0
        self.data.gcodeIndex = 0
        self.data.quick_queue.put("STOP") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        print("Gode Stopped")
    
    def textInputPopup(self, target):
        
        self.targetWidget = target
        
        self.popupContent = TouchNumberInput(done=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        
        self.targetWidget.text = self.popupContent.textInput.text
        self._popup.dismiss()