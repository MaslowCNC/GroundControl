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
        self.data.bind(uploadFlag       = self.onUploadFlagChange)
    
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
        self.percentComplete = '%.1f' %(100* (float(newIndex) / (len(self.data.gcode)-1))) + "%"
    
    def onGcodeFileChange(self, callback, newGcode):
    
        #reset the shift values to 0 because the new gcode is not loaded with a shift applied
        #self.shiftX = 0
        #self.shiftY = 0
        
        #reset the gcode index to the beginning and update the display
        #self.data.gcodeIndex = 0
        #self.moveGcodeIndex(0)
        
        pass
    
    def onUploadFlagChange(self, callback, newFlagValue):
        if self.data.uploadFlag is 0 and self.data.gcodeIndex > 1: #if the machine is stopped partway through a file
            self.holdBtn.text = "CONTINUE"
        else:
            self.holdBtn.text = "HOLD"
    
    def moveGcodeIndex(self, dist):
        '''
        Move the gcode index by a dist number of lines
        '''
        maxIndex = len(self.data.gcode)-1
        targetIndex = self.data.gcodeIndex + dist
        
        #check to see if we are still within the length of the file
        if targetIndex < 0:             #negative index not allowed 
            self.data.gcodeIndex = 0
        elif maxIndex < 0:              #break if there is no data to read
            return
        elif targetIndex > maxIndex:    #reading past the end of the file is not allowed
            self.data.gcodeIndex = maxIndex
        else:
            self.data.gcodeIndex = targetIndex
        
        gCodeLine = self.data.gcode[self.data.gcodeIndex]
        
        xTarget = 0
        yTarget = 0
        
        try:
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
        except:
            print "Unable to update position for new gcode line"
    
    def pause(self):
        if  self.holdBtn.text == "HOLD":
            self.data.uploadFlag = 0
            print("Run Paused")
        else:
            self.data.uploadFlag = 1
            print("Run Resumed")
    
    def jmpsize(self):
        try:
            self.stepsizeval = float(self.moveDistInput.text)
        except:
            pass
    
    def test(self):
        print "test has no current function"
    
    def upLeft(self):
        self.jmpsize()
        xtarget = self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget
        
    def upRight(self):
        self.jmpsize()
        xtarget = self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def up(self):
        self.jmpsize()
        target = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 Y" + str(target) + " ")
        self.target[1] = target

    def left(self):
        self.jmpsize()
        target = self.target[0] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(target) + " ")
        self.target[0] = target
        
    def right(self):
        self.jmpsize()
        target = self.target[0] + float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(target) + " ")
        self.target[0] = target
        
    def downLeft(self):
        self.jmpsize()
        xtarget = self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def down(self):
        self.jmpsize()
        target = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 Y" + str(target) + " ")
        self.target[1] = target

    def downRight(self):
        self.jmpsize()
        xtarget = self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G00 X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = xtarget
        self.target[1] = ytarget

    def zUp(self):
        self.jmpsize()
        target = self.target[2] + 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 Z" + str(target) + " ")
        self.target[2] = self.target[2] + 0.10*float(self.stepsizeval)

    def zDown(self):
        self.jmpsize()
        target = self.target[2] - 0.10*float(self.stepsizeval)
        self.data.gcode_queue.put("G00 Z" + str(target) + " ")
        self.target[2] = self.target[2] - 0.10*float(self.stepsizeval)

    def zeroZ(self):
        self.data.gcode_queue.put("G10 Z0 ")
        self.target[2] = 0
        
    def home(self):
        
        if self.units == "INCHES":
            self.data.gcode_queue.put("G00 Z.25 ")
        else:
            self.data.gcode_queue.put("G00 Z5.0 ")
        
        self.data.gcode_queue.put("G00 X" + str(self.shiftX) + " Y" + str(self.shiftY) + " ")
        
        self.data.gcode_queue.put("G00 Z0 ")
        
        self.target[0] = self.shiftX
        self.target[1] = self.shiftY
        self.target[2] = 0.0
    
    def moveOrigin(self):
        '''
        
        Move the gcode origin to the current location
        
        '''
        self.data.gcodeShift = [self.numericalPosX,self.numericalPosY]
    
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
        self.onUploadFlagChange(self.stopRun, 0)
        print("Gode Stopped")
    
    def textInputPopup(self, target):
        
        self.targetWidget = target
        
        self.popupContent = TouchNumberInput(done=self.dismiss_popup)
        self._popup = Popup(title="Change increment size of machine movement", content=self.popupContent,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        try:
            float(self.popupContent.textInput.text)
            self.targetWidget.text = self.popupContent.textInput.text
        except:
            pass                                                             #If what was entered cannot be converted to a number, leave the value the same
        self._popup.dismiss()