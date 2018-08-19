from time                                             import time
from kivy.properties                                  import ObjectProperty
from kivy.properties                                  import StringProperty
from kivy.properties                                  import BooleanProperty
from kivy.properties                                  import OptionProperty
from kivy.properties                                  import NumericProperty
from kivy.event                                       import EventDispatcher
from DataStructures.logger                            import   Logger
from DataStructures.loggingQueue                      import   LoggingQueue
import Queue

class Data(EventDispatcher):
    '''

    Data is a set of variables which are essentially global variables which hold information 
    about the gcode file opened, the machine which is connected, and the user's settings. These 
    variables are NOT thread-safe. The queue system should always be used for passing information 
    between threads.

    '''
    
    
    '''
    Data available to all widgets
    '''
    
    #Gcodes contains all of the lines of gcode in the opened file
    gcode      = ObjectProperty([])
    version    = '1.19'
    #all of the available COM ports
    comPorts   = []
    #This defines which COM port is used
    comport    = StringProperty("")
    #The index of the next unread line of Gcode
    gcodeIndex = NumericProperty(0)
    #Index of changes in z
    zMoves     = ObjectProperty([])
    #Holds the current value of the feed rate
    feedRate   = 20
    #holds the address of the g-code file so that the gcode can be refreshed
    gcodeFile  = StringProperty("")
    #the current position of the cutting head
    currentpos = [0.0, 0.0, 0.0]
    target     = [0.0, 0.0, 0.0]
    units      = OptionProperty("MM", options=["MM", "INCHES"])
    tolerance  = NumericProperty(0.5)
    gcodeShift = ObjectProperty([0.0,0.0])                          #the amount that the gcode has been shifted
    logger     =  Logger()                                          #the module which records the machines behavior to review later
    
    # Background image stuff, persist but not saved
    backgroundFile = None
    backgroundTexture = None
    backgroundManualReg = []
    backgroundRedraw = BooleanProperty(False)
    
    '''
    Flags
    '''
    #sets a flag if the gcode is being uploaded currently
    uploadFlag = BooleanProperty(0)
    #this is used to determine the first time the position is received from the machine
    firstTimePosFlag = 0
    #report if the serial connection is open
    connectionStatus = BooleanProperty(0)
    #is the calibration process currently underway 0 -> false
    calibrationInProcess = False
    
    '''
    Pointers to Objects
    '''
    config = None #pointer to the program configuration object...used for writing to settings
    serialPort = None #this is a pointer to the program serial port object
    
    '''
    
    Colors
    
    '''
    fontColor                                             =  StringProperty('[color=7a7a7a]')
    drawingColor                                          =  ObjectProperty([.47,.47,.47])
    iconPath                                              =  StringProperty('./Images/Icons/normal/')
    posIndicatorColor                                     =  ObjectProperty([0,0,0])
    targetInicatorColor                                   =  ObjectProperty([1,0,0])

    '''
    Misc UI bits that need to be saved between invocations (but not saved)
    '''
    zPush = None
    zPushUnits = 'MM'
    zReadoutPos = 0.00
    zPopupUnits = None
    zStepSizeVal = 0.1
    
    '''
    Queues
    '''
    message_queue   =  LoggingQueue(logger)
    gcode_queue     =  Queue.Queue()
    quick_queue     =  Queue.Queue()
    
    def __init__(self):
        '''
        
        Initializations.
        
        '''
        self.logger.data = self
