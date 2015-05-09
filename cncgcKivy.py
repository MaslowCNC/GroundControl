'''

Kivy Imports

'''
from kivy.app import App
from kivy.properties import OptionProperty, NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse
from kivy.graphics import InstructionGroup
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

'''

Other Imports

'''

import threading
import Queue
import serial
from time import time
import sys

'''

UI Elements

'''

class GcodeCanvas(FloatLayout):
    pass

class FrontPage(Screen):
    exploreplot = ObjectProperty(None)
    exampleplot = ObjectProperty(None)
    
    def testFuncOne(self):
        print "func one"
        
    def testFuncTwo(self):
        print "func two"

class OtherFeatures(Screen):
    pass

class SoftwareSettings(Screen):
    pass

class ViewMenu(GridLayout):
    pass

class RunMenu(FloatLayout):
    pass

class ConnectMenu(FloatLayout):
    
    connectmenu = ObjectProperty(None) #make ConnectMenu object accessable at this scope
    comPorts = []
    
    
    def reconnect(self):
        print "reconnect pressed"
    
        '''
    
    Serial Connection Functions
    
    '''
    
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
        
        print self.comPorts
    
    

class Diagnostics(FloatLayout):
    pass

class ManualControl(FloatLayout):
    pass

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
        
        Clock.schedule_interval(self.otherfeatures.connectmenu.detectCOMports, 2)
        
        return interface
    
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
