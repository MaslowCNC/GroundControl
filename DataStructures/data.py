from time                                             import time
from kivy.properties                                  import ObjectProperty
from kivy.event                                       import EventDispatcher
import Queue

class Data(EventDispatcher):
    '''

    Data is a set of variables which are essentially global variables which hold information 
    about the gcode file opened, the machine which is connected, and the user's settings. These 
    variables are NOT thread-safe. The queue system should always be used for passing information 
    between threads.

    '''
    
    '''
    Things I would like to delete
    '''
    #A flag to indicate if logging is enabled
    logflag = 0
    #A flag to indicate if the main window should auto scroll
    scrollFlag = 1
    #The file where logging will take place if it is turned on
    logfile = None
    #The amount to move from one step
    stepsizeval = 1
    #click values for drag window
    xclickstart = 0
    xclickend = 0
    yclickstart = 0
    yclickend = 0
    offsetX = 0
    offsetY = 0 #was -200 
    #Zoom level
    zoomLevel = 4.9 #4.9 is real size on my monitor
    unitsScale = 1/1.27 #this sets the values for inches and mm 
    #Tool Width and Color Flags
    toolWidthFlag = 0
    colorFlag = 0
    spindleFlag = 1
    prependString = " "
    absoluteFlag = 1
    unitsSetFlag = 0 #used once to set the correct units on the machine
    startTime = 0
    endTime = 0
    xDrag = 0
    yDrag = 0
    saveFlag = 1 #program saves when flag is 1
    appData = ""
    contrast = 50
    backlight = 65
    heartBeat = time()
    
    
    '''
    Data available to all widgets
    '''
    #Gcodes contains all of the lines of gcode in the opened file
    gcode = ObjectProperty([])
    version = '0.60'
    #all of the available COM ports
    comPorts = []
    #This defines which COM port is used
    comport = "COM4"
    #The index of the next unread line of Gcode
    gcodeIndex = 0
    #Holds the current value of the feed rate
    feedRate = 20
    #holds the address of the g-code file so that the gcode can be refreshed
    gcodeFile = ""
    #the current position of the cutting head
    currentpos = [0.0, 0.0, 0.0]
    target = [0.0, 0.0, 0.0]
    firstTimePosFlag = 0 #this is used to determine the first time the position is received from the machine
    
    '''
    Flags
    '''
    #sets a flag if the gcode is being uploaded currently
    uploadFlag = 0
    #flag is 1 if the machine is ready for a command
    readyFlag = 0
    
    '''
    Pointers to Objects
    '''
    config = None #pointer to the program configuration object...used for writing to settings
    serialPort = None #this is a pointer to the program serial port object
    
    '''
    Queues
    '''
    message_queue   =  Queue.Queue()
    gcode_queue     =  Queue.Queue()
    quick_queue     =  Queue.Queue()
