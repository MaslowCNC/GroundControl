'''

This module defines the appearence and funcition of the front page of the program.

This page is used to manually move the machine, see the positional readout, and view the file being cut

'''

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty

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
    
    def reZero(self): 
        self.target = [0,0,0]
        
        self.xReadoutPos = "0 mm"
        self.yReadoutPos = "0 mm"
        self.zReadoutPos = "0 mm"
        
        self.gcodecanvas.setCrossPos(0,0)
        
        self.gcode_queue.put("G10 X0 Y0 Z0 ")
    
    def startRun(self):
        self.reZero()
        
        self.gcodecanvas.uploadFlag = 1
    
    def sendLine(self):
        try:
            self.gcode_queue.put(self.gcodecanvas.gcode[self.gcodecanvas.gcodePos])
            self.gcodecanvas.gcodePos = self.gcodecanvas.gcodePos + 1
        except:
            print "gcode run complete"
    
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
