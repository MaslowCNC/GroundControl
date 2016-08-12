'''

This module defines the appearance and function of the front page of the program.

This page is used to manually move the machine, see the positional readout, and view the file being cut

'''

from kivy.uix.screenmanager                    import Screen
from kivy.properties                           import ObjectProperty, StringProperty
from DataStructures.makesmithInitFuncs         import MakesmithInitFuncs

class FrontPage(Screen, MakesmithInitFuncs):
    textconsole    = ObjectProperty(None)
    connectmenu    = ObjectProperty(None) #make ConnectMenu object accessible at this scope
    gcodecanvas    = ObjectProperty(None) 
    screenControls = ObjectProperty(None) 
    
    target = [0,0,0]
    
    distMove = 0
    speedMove = 0
    
    connectionStatus = StringProperty("Not Connected")
    
    xReadoutPos = StringProperty("0 mm")
    yReadoutPos = StringProperty("0 mm")
    zReadoutPos = StringProperty("0 mm")
    
    stepsizeval = 0
    feedRate = 0
    
    spindleFlag = 0
    
    consoleText = StringProperty(" ")
    
    def setPosReadout(self, xPos, yPos, zPos, units):
        self.xReadoutPos = str(xPos) + " " + units
        self.yReadoutPos = str(yPos) + " " + units
        self.zReadoutPos = str(zPos) + " " + units
    
    def setUpData(self, data):
        self.data = data
        print "Initialized: " + str(self)
        self.gcodecanvas.setUpData(data)
        self.screenControls.setUpData(data)
    
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
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)
        
    def upRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def up(self):
        self.jmpsize()
        target = self.target[1] + float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] + float(self.stepsizeval)

    def left(self):
        self.jmpsize()
        target = -1*self.target[0] - float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        
    def right(self):
        self.jmpsize()
        target = -1*self.target[0] + float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(target) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        
    def downLeft(self):
        self.jmpsize()
        xtarget = -1*self.target[0] - float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] + float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)    

    def down(self):
        self.jmpsize()
        target = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Y" + str(target) + " ")
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def downRight(self):
        self.jmpsize()
        xtarget = -1*self.target[0] + float(self.stepsizeval)
        ytarget = self.target[1] - float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X" + str(xtarget) + " Y" + str(ytarget) + " ")
        self.target[0] = self.target[0] - float(self.stepsizeval)
        self.target[1] = self.target[1] - float(self.stepsizeval)

    def zUp(self):
        self.jmpsize()
        target = self.target[2] + float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] + float(self.stepsizeval)

    def zDown(self):
        self.jmpsize()
        target = self.target[2] - float(self.stepsizeval)
        self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z" + str(target) + " ")
        self.target[2] = self.target[2] - float(self.stepsizeval)

    def home(self):
        if self.target[2] < 0:
            self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z0 ")
            self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X0 Y0 Z0 ")
        if self.target[2] >= 0:
            self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " X0 Y0 ")
            self.data.gcode_queue.put("G01 F" + str(float(self.feedRate)) + " Z0 ")
        self.target[0] = 0.0
        self.target[1] = 0.0
        self.target[2] = 0.0
    
    def reZero(self): 
        self.target = [0,0,0]
        
        self.data.gcode_queue.put("G10 X0 Y0 Z0 ")
    
    def startRun(self):
        self.reZero()
        
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
    
    def toggleSpindle(self):
    #toggleSpindle turns on and off the dremel if a relay is attached
        if(self.spindleFlag == 1):
            self.data.gcode_queue.put("S5000 ")
            self.spindleFlag = 0
        elif(self.dataBack.spindleFlag == 0):
            self.data.gcode_queue.put("S0 ")
            self.spindleFlag = 1
