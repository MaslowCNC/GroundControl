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
    comPort = ""
    
    message_queue = Queue.Queue()
    gcode_queue = Queue.Queue()
    quick_queue = Queue.Queue()
    
    def reconnect(self):
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
        print(self.comport)
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
                    #print("no read")
                try:
                    msg = msg.decode('utf-8')
                except:
                    pass
                    #print("decode issue")
                    
                if len(msg) > 0:
                    
                    print "heardback:"
                    print msg
                    
                    if msg == "gready\r\n":
                        #print("ready set")
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
                        #print(len(gcode))
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
                    #print("gcode seen")
                    gcode = gcode.encode()
                    #print(len(gcode))
                    print("Sending: ")
                    print(gcode)
                    try:
                        serialCAN.write(gcode)
                        gcode = ""  
                    except:
                        print("write issue")
                    #print("end")
                    subReadyFlag = False
                else:
                    pass


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
        Clock.schedule_interval(self.runPeriodically, .1)
        
        return interface
    
    '''
    
    Update Functions
    
    '''
    
    def runPeriodically(self, *args):
        if not self.otherfeatures.connectmenu.message_queue.empty(): #if there is new data to be read
            message = self.otherfeatures.connectmenu.message_queue.get()
            print "Message in main thread:"
            print message
    
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
