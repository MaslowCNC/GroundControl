'''

Kivy Imports

'''
from kivy.config                import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'minimum_width', '620')
Config.set('graphics', 'minimum_height', '440')
Config.set('kivy', 'exit_on_escape', '0')
from kivy.app                   import App
from kivy.uix.gridlayout        import GridLayout
from kivy.uix.floatlayout       import FloatLayout
from kivy.uix.anchorlayout      import AnchorLayout
from kivy.core.window           import Window
from kivy.uix.button            import Button
from kivy.clock                 import Clock
from kivy.uix.popup             import Popup
import math
import global_variables
import sys


'''

Internal Module Imports

'''

from UIElements.frontPage         import   FrontPage
from UIElements.screenControls    import   ScreenControls
from UIElements.gcodeCanvas       import   GcodeCanvas
from UIElements.otherFeatures     import   OtherFeatures
from UIElements.softwareSettings  import   SoftwareSettings
from UIElements.viewMenu          import   ViewMenu
from UIElements.runMenu           import   RunMenu
from UIElements.connectMenu       import   ConnectMenu
from UIElements.diagnosticsMenu   import   Diagnostics
from UIElements.manualControls    import   ManualControl
from DataStructures.data          import   Data
from Connection.nonVisibleWidgets import   NonVisibleWidgets
from UIElements.notificationPopup import   NotificationPopup
'''

Main UI Program

'''

class GroundControlApp(App):

    def get_application_config(self):
        return super(GroundControlApp, self).get_application_config(
            '~/%(appname)s.ini')

    json = '''
    [
        {
            "type": "string",
            "title": "Serial Connection",
            "desc": "Select the COM port to connect to machine",
            "section": "Maslow Settings",
            "key": "COMport"
        },
        {
            "type": "string",
            "title": "Distance Between Motors",
            "desc": "The horizontal distance between the center of the motor shafts in MM.\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "motorSpacingX"
            
        },
        {
            "type": "string",
            "title": "Work Area Width in MM",
            "desc": "The width of the machine working area (normally 8 feet).\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "bedWidth"
        },
        {
            "type": "string",
            "title": "Work Area Height in MM",
            "desc": "The Height of the machine working area (normally 4 feet).\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "bedHeight"
        },
        {
            "type": "string",
            "title": "Motor Offset Height in MM",
            "desc": "The vertical distance from the edge of the work area to the level of the motors.\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "motorOffsetY"
        },
        {
            "type": "string",
            "title": "Distance Between Sled Mounting Points",
            "desc": "The horizontal distance between the points where the chains mount to the sled.\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "sledWidth"
        },
        {
            "type": "string",
            "title": "Vertical Distance Sled Mounts to Cutter",
            "desc": "The vertical distance between where the chains mount on the sled to the cutting tool.\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "sledHeight"
        },
        {
            "type": "string",
            "title": "Center Of Gravity",
            "desc": "How far below the cutting bit is the center of gravity. This can be found by resting the sled on a round object and observing where it balances.\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "sledCG"
        },
        {
            "type": "bool",
            "title": "z-axis installed",
            "desc": "Does the machine have an automatic z-axis?\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "zAxis"
        },
        {
            "type": "string",
            "title": "Z-Axis Pitch",
            "desc": "The number of mm moved per rotation of the z-axis\\ndefault setting: %s",
            "section": "Maslow Settings",
            "key": "zDistPerRot"
        },
        {
            "type": "options",
            "title": "Color Scheme",
            "desc": "Switch between the light and dark color schemes. Restarting GC is needed for this change to take effect\\ndefault setting: %s",
            "options": ["Light", "Dark"],
            "section": "Maslow Settings",
            "key": "colorScheme"
        },
        {
            "type": "string",
            "title": "Open File",
            "desc": "The path to the open file\\ndefault setting: your home directory",
            "section": "Maslow Settings",
            "key": "openFile"
        },
        {
            "type": "string",
            "title": "Macro 1",
            "desc": "User defined gcode bound to the Macro 1 button",
            "section": "Maslow Settings",
            "key": "macro1"
        },
        {
            "type": "string",
            "title": "Macro 1 Title",
            "desc": "User defined title for the Macro 1 button",
            "section": "Maslow Settings",
            "key": "macro1_title"
        },
        {
            "type": "string",
            "title": "Macro 2",
            "desc": "User defined gcode bound to the Macro 2 button",
            "section": "Maslow Settings",
            "key": "macro2"
        },
        {
            "type": "string",
            "title": "Macro 2 Title",
            "desc": "User defined title for the Macro 2 button",
            "section": "Maslow Settings",
            "key": "macro2_title"
        }
    ]
    ''' % (
        # global_variables._COMport, 
        global_variables._motorSpacingX, 
        global_variables._bedWidth,
        global_variables._bedHeight,
        global_variables._motorOffsetY,
        global_variables._sledWidth,
        global_variables._sledHeight,
        global_variables._sledCG,
        global_variables._zAxis,
        global_variables._zDistPerRot,
        global_variables._colorScheme
        )

    advanced = '''
    [
        {
            "type": "string",
            "title": "Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the left or right motor\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "encoderSteps"
        },
        {
            "type": "string",
            "title": "Gear Teeth",
            "desc": "The number of teeth on the gear of the left or right motor\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "gearTeeth"
        },
        {
            "type": "string",
            "title": "Chain Pitch",
            "desc": "The distance between chain roller centers\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "chainPitch"
        },
        {
            "type": "string",
            "title": "Z-Axis Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the z-axis\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "zEncoderSteps"
        },
        {
            "type": "bool",
            "title": "Spindle Automation",
            "desc": "Should the spindle start and stop automatically based on gcode? Leave off for default stepper control.\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "zAxisAuto"
        },
        {
            "type": "string",
            "title": "Home Position X Coordinate",
            "desc": "The X coordinate of the home position\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "homeX"
        },
        {
            "type": "string",
            "title": "Home Position Y Coordinate",
            "desc": "The X coordinate of the home position\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "homeY"
        },
        {
            "type": "bool",
            "title": "Truncate Floating Point Numbers",
            "desc": "Truncate floating point numbers at the specified number of decimal places\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "truncate"
        },
        {
            "type": "string",
            "title": "Floating Point Precision",
            "desc": "If truncate floating point numbers is enabled, the number of digits after the decimal place to preserve\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "digits"
        },
        {
            "type": "options",
            "title": "Kinematics Type",
            "desc": "Switch between trapezoidal and triangular kinematics\\ndefault setting: %s",
            "options": ["Quadrilateral", "Triangular"],
            "section": "Advanced Settings",
            "key": "kinematicsType"
        },
        {
            "type": "string",
            "title": "Rotation Radius for Triangular Kinematics",
            "desc": "The distance between where the chains attach and the center of the router bit in mm\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "rotationRadius"
        },
        {
            "type": "bool",
            "title": "Enable Custom Positional PID Values",
            "desc": "Enable using custom values for the positional PID controller. Turning this off will return to the default values\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "enablePosPIDValues"
        },
        {
            "type": "string",
            "title": "Kp Position",
            "desc": "The proportional constant for the position PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KpPos"
        },
        {
            "type": "string",
            "title": "Ki Position",
            "desc": "The integral constant for the position PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KiPos"
        },
        {
            "type": "string",
            "title": "Kd Position",
            "desc": "The derivative constant for the position PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KdPos"
        },
        {
            "type": "string",
            "title": "Proportional Weighting",
            "desc": "The ratio of Proportional on Error (1) to Proportional on Measure (0)\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "propWeight"
        },
        {
            "type": "bool",
            "title": "Enable Custom Velocity PID Values",
            "desc": "Enable using custom values for the Velocity PID controller. Turning this off will return to the default values\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "enableVPIDValues"
        },
        {
            "type": "string",
            "title": "Kp Velocity",
            "desc": "The proportional constant for the velocity PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KpV"
        },
        {
            "type": "string",
            "title": "Ki Velocity",
            "desc": "The integral constant for the velocity PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KiV"
        },
        {
            "type": "string",
            "title": "Kd Velocity",
            "desc": "The derivative constant for the velocity PID controller\\ndefault setting: %s",
            "section": "Advanced Settings",
            "key": "KdV"
        }
    ]
    ''' % (
        global_variables._encoderSteps,
        global_variables._gearTeeth,
        global_variables._chainPitch,
        global_variables._zEncoderSteps,
        global_variables._zAxisAuto,
        global_variables._homeX,
        global_variables._homeY,
        global_variables._truncate,
        global_variables._digits,
        global_variables._kinematicsType,
        global_variables._rotationRadius,
        global_variables._enablePosPIDValues,
        global_variables._KpPos,
        global_variables._KiPos,
        global_variables._KdPos,
        global_variables._propWeight,
        global_variables._enableVPIDValues,
        global_variables._KpV,
        global_variables._KiV,
        global_variables._KdV
        )
    
    gcsettings = '''
    [
        {
            "type": "bool",
            "title": "Center Canvas on Window Resize",
            "desc": "When resizing the window, automatically reset the Gcode canvas to be centered and zoomed out. Program must be restarted to take effect.\\ndefault setting: %s",
            "section": "Ground Control Settings",
            "key": "centerCanvasOnResize"
        },
        {
            "type": "string",
            "title": "Zoom In",
            "desc": "Pressing this key will zoom in. Note combinations of keys like \'shift\' + \'=\' may not work as expected. Program must be restarted to take effect.\\ndefault setting: %s",
            "section": "Ground Control Settings",
            "key": "zoomIn"
        },
        {
            "type": "string",
            "title": "Zoom Out",
            "desc": "Pressing this key will zoom in. Note combinations of keys like \'shift\' + \'=\' may not work as expected. Program must be restarted to take effect.\\ndefault setting: %s",
            "section": "Ground Control Settings",
            "key": "zoomOut"
        },
        {
            "type": "string",
            "title": "Valid File Extensions",
            "desc": "Valid file extensions for Ground Control to open. Comma separated list.\\ndefault setting: %s",
            "section": "Ground Control Settings",
            "key": "validExtensions"
        }
    ]
    ''' % (
        global_variables._centerCanvasOnResize,
        global_variables._zoomIn,
        global_variables._zoomOut,
        global_variables._validExtensions
        )
    
    def build(self):
        
        interface       =  FloatLayout()
        self.data       =  Data()
        
        if self.config.get('Maslow Settings', 'colorScheme') == 'Light':
            self.data.iconPath               = './Images/Icons/normal/'
            self.data.fontColor              = '[color=7a7a7a]'
            self.data.drawingColor           = [.47,.47,.47]
            Window.clearcolor                = (1, 1, 1, 1)
            self.data.posIndicatorColor      =  [0,0,0]
            self.data.targetInicatorColor    =  [1,0,0]
        elif self.config.get('Maslow Settings', 'colorScheme') == 'Dark':
            self.data.iconPath               = './Images/Icons/highvis/'
            self.data.fontColor              = '[color=000000]'
            self.data.drawingColor           = [1,1,1]
            Window.clearcolor                = (0, 0, 0, 1)
            self.data.posIndicatorColor      =  [1,1,1]
            self.data.targetInicatorColor    =  [1,0,0]
        
        
        Window.maximize()
        
        
        self.frontpage = FrontPage(self.data, name='FrontPage')
        interface.add_widget(self.frontpage)
        
        self.nonVisibleWidgets = NonVisibleWidgets()
        
        
        '''
        Load User Settings
        '''
        
        if self.config.get('Advanced Settings', 'encoderSteps') == '8148.0':
            self.data.message_queue.put("Message: This update will adjust the the number of encoder pulses per rotation from 8,148 to 8,113 in your settings which improves the positional accuracy.\n\nPerforming a calibration will help you get the most out of this update.")
            self.config.set('Advanced Settings', 'encoderSteps', '8113.73')
            self.config.write()
        
        self.data.comport = self.config.get('Maslow Settings', 'COMport')
        self.data.gcodeFile = self.config.get('Maslow Settings', 'openFile')
        offsetX = float(self.config.get('Advanced Settings', 'homeX'))
        offsetY = float(self.config.get('Advanced Settings', 'homeY'))
        self.data.gcodeShift = [offsetX,offsetY]
        self.data.config  = self.config
        
        '''
        Initializations
        '''
        
        self.frontpage.setUpData(self.data)
        self.nonVisibleWidgets.setUpData(self.data)
        self.frontpage.gcodecanvas.initialize()
        
        '''
        Scheduling
        '''
        
        Clock.schedule_interval(self.runPeriodically, .01)
        
        '''
        Push settings to machine
        '''
        self.data.bind(connectionStatus = self.push_settings_to_machine)
        self.data.pushSettings = self.push_settings_to_machine
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the config sections.
        """
        config.setdefaults('Maslow Settings', {'COMport'              : global_variables._COMport,
                                               'zAxis'                : global_variables._zAxis,
                                               'zDistPerRot'          : global_variables._zDistPerRot,
                                               'bedWidth'             : global_variables._bedWidth,
                                               'bedHeight'            : global_variables._bedHeight,
                                               'motorOffsetY'         : global_variables._motorOffsetY,
                                               'motorSpacingX'        : global_variables._motorSpacingX,
                                               'sledWidth'            : global_variables._sledWidth,
                                               'sledHeight'           : global_variables._sledHeight,
                                               'sledCG'               : global_variables._sledCG,
                                               'colorScheme'          : global_variables._colorScheme,
                                               'openFile'             : global_variables._openFile,
                                               'macro1'               : global_variables._macro1,
                                               'macro1_title'         : global_variables._macro1_title,
                                               'macro2'               : global_variables._macro2,
                                               'macro2_title'         : global_variables._macro2_title})

        config.setdefaults('Advanced Settings', {'encoderSteps'       : global_variables._encoderSteps,
                                                 'gearTeeth'          : global_variables._gearTeeth,
                                                 'chainPitch'         : global_variables._chainPitch,
                                                 'zEncoderSteps'      : global_variables._zEncoderSteps,
                                                 'zAxisAuto'          : global_variables._zAxisAuto,
                                                 'homeX'              : global_variables._homeX,
                                                 'homeY'              : global_variables._homeY,
                                                 'truncate'           : global_variables._truncate,
                                                 'digits'             : global_variables._digits,
                                                 'kinematicsType'     : global_variables._kinematicsType,
                                                 'rotationRadius'     : global_variables._rotationRadius,
                                                 'enablePosPIDValues' : global_variables._enablePosPIDValues,
                                                 'KpPos'              : global_variables._KpPos,
                                                 'KiPos'              : global_variables._KiPos,
                                                 'KdPos'              : global_variables._KdPos,
                                                 'propWeight'         : global_variables._propWeight,
                                                 'enableVPIDValues'   : global_variables._enableVPIDValues,
                                                 'KpV'                : global_variables._KpV,
                                                 'KiV'                : global_variables._KiV,
                                                 'KdV'                : global_variables._KdV})

        config.setdefaults('Ground Control Settings', {'centerCanvasOnResize'   : global_variables._centerCanvasOnResize,
                                                       'zoomIn'                 : global_variables._zoomIn,
                                                       'zoomOut'                : global_variables._zoomOut,
                                                       'validExtensions'        : global_variables._validExtensions,})

    def build_settings(self, settings):
        """
        Add custom section to the default configuration object.
        """
        settings.add_json_panel('Maslow Settings', self.config, data=self.json)
        settings.add_json_panel('Advanced Settings', self.config, data=self.advanced)
        settings.add_json_panel('Ground Control Settings', self.config, data=self.gcsettings)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        
        if section == "Maslow Settings":
            
            self.push_settings_to_machine()
            
            if key == "COMport":
                self.data.comport = value
            
            if (key == "bedHeight" or key == "bedWidth"):
                self.frontpage.gcodecanvas.drawWorkspace()

            if (key == "macro1_title") or (key == "macro2_title"):
                self.frontpage.update_macro_titles()

        if section == "Advanced Settings":
            
            self.push_settings_to_machine()
            
            if (key == "truncate") or (key == "digits"):
                self.frontpage.gcodecanvas.reloadGcode()
    
    def push_settings_to_machine(self, *args):
        
        #Push motor configuration settings to machine
        
        if self.data.connectionStatus != 1:
            return # only run on connection true
        
        if int(self.data.config.get('Advanced Settings', 'enablePosPIDValues')) == 1:
            KpPos = float(self.data.config.get('Advanced Settings', 'KpPos'))
            KiPos = float(self.data.config.get('Advanced Settings', 'KiPos'))
            KdPos = float(self.data.config.get('Advanced Settings', 'KdPos'))
            propWeight = float(self.data.config.get('Advanced Settings', 'propWeight'))
        else:
            KpPos = 1300
            KiPos = 0
            KdPos = 34
            propWeight = 1
        
        if int(self.data.config.get('Advanced Settings', 'enableVPIDValues')) == 1:
            KpV = float(self.data.config.get('Advanced Settings', 'KpV'))
            KiV = float(self.data.config.get('Advanced Settings', 'KiV'))
            KdV = float(self.data.config.get('Advanced Settings', 'KdV'))
        else:
            KpV = 7
            KiV = 0
            KdV = .28
        
        # Be pretty dumb about this, just push settings without checking to 
        # see what machine has
        
        self.data.gcode_queue.put("$16=" + str(self.data.config.get('Maslow Settings', 'zAxis')))
        self.data.gcode_queue.put("$12=" + str(self.data.config.get('Advanced Settings', 'encoderSteps')))
        distPerRot = float(self.data.config.get('Advanced Settings', 'gearTeeth')) * float(self.data.config.get('Advanced Settings', 'chainPitch'))
        self.data.gcode_queue.put("$13=" + str(distPerRot))
        self.data.gcode_queue.put("$19=" + str(self.data.config.get('Maslow Settings'  , 'zDistPerRot')))
        self.data.gcode_queue.put("$20=" + str(self.data.config.get('Advanced Settings', 'zEncoderSteps')))
        
        #main axes
        self.data.gcode_queue.put("$21=" + str(KpPos))
        self.data.gcode_queue.put("$22=" + str(KiPos))
        self.data.gcode_queue.put("$23=" + str(KdPos))
        self.data.gcode_queue.put("$24=" + str(propWeight))
        self.data.gcode_queue.put("$25=" + str(KpV))
        self.data.gcode_queue.put("$26=" + str(KiV))
        self.data.gcode_queue.put("$27=" + str(KdV))
        self.data.gcode_queue.put("$28=1.0")
        
        #z axis
        self.data.gcode_queue.put("$29=" + str(KpPos))
        self.data.gcode_queue.put("$30=" + str(KiPos))
        self.data.gcode_queue.put("$31=" + str(KdPos))
        self.data.gcode_queue.put("$32=" + str(propWeight))
        self.data.gcode_queue.put("$33=" + str(KpV))
        self.data.gcode_queue.put("$34=" + str(KiV))
        self.data.gcode_queue.put("$35=" + str(KdV))
        self.data.gcode_queue.put("$36=1.0")
        self.data.gcode_queue.put("$17=" + str(self.data.config.get('Advanced Settings', 'zAxisAuto')))
        
        #Push kinematics settings to machine
        if self.data.config.get('Advanced Settings', 'kinematicsType') == 'Quadrilateral':
            kinematicsType = 1
        else:
            kinematicsType = 2
        
        self.data.gcode_queue.put("$0=" + str(self.data.config.get('Maslow Settings', 'bedWidth')))
        self.data.gcode_queue.put("$1=" + str(self.data.config.get('Maslow Settings', 'bedHeight')))
        self.data.gcode_queue.put("$2=" + str(self.data.config.get('Maslow Settings', 'motorSpacingX')))
        self.data.gcode_queue.put("$3=" + str(self.data.config.get('Maslow Settings', 'motorOffsetY')))
        self.data.gcode_queue.put("$4=" + str(self.data.config.get('Maslow Settings', 'sledWidth')))
        self.data.gcode_queue.put("$5=" + str(self.data.config.get('Maslow Settings', 'sledHeight')))
        self.data.gcode_queue.put("$6=" + str(self.data.config.get('Maslow Settings', 'sledCG')))
        self.data.gcode_queue.put("$7=" + str(kinematicsType))
        self.data.gcode_queue.put("$8=" + str(self.data.config.get('Advanced Settings', 'rotationRadius')))

        
        # Force kinematics recalibration
        self.data.gcode_queue.put("$K")
        
    '''
    
    Update Functions
    
    '''
    
    def writeToTextConsole(self, message):
        try:
            newText = self.frontpage.consoleText[-500:] + message
            self.frontpage.consoleText = newText
            self.frontpage.textconsole.gotToBottom()  
        except:
            self.frontpage.consoleText = "text not displayed correctly"
    
    def runPeriodically(self, *args):
        '''
        this block should be handled within the appropriate widget
        '''
        while not self.data.message_queue.empty(): #if there is new data to be read
            message = self.data.message_queue.get()
            
            if message[0] == "<":
                self.setPosOnScreen(message)
            elif message[0] == "[":
                if message[1:4] == "PE:":
                    self.setErrorOnScreen(message)
                elif message[1:8] == "Measure":
                    print "measure seen"
                    print message
                    measuredDist = float(message[9:len(message)-3])
                    self.data.measureRequest(measuredDist)
            elif message[0:13] == "Maslow Paused":
                self.data.uploadFlag = 0
                self.writeToTextConsole(message)
            elif message[0:8] == "Message:":
                self.previousUploadStatus = self.data.uploadFlag 
                self.data.uploadFlag = 0
                try:
                    self._popup.dismiss()                                           #close any open popup
                except:
                    pass                                                            #there wasn't a popup to close
                content = NotificationPopup(continueOn = self.dismiss_popup_continue, text = message[9:])
                if sys.platform.startswith('darwin'):
                    self._popup = Popup(title="Notification: ", content=content,
                            auto_dismiss=False, size=(360,240), size_hint=(.3, .3))
                else:
                    self._popup = Popup(title="Notification: ", content=content,
                            auto_dismiss=False, size=(360,240), size_hint=(None, None))
                self._popup.open()
                if global_variables._keyboard:
                    global_variables._keyboard.bind(on_key_down=self.keydown_popup)
                    self._popup.bind(on_dismiss=self.ondismiss_popup)
            elif message[0:8] == "Firmware":
                self.data.logger.writeToLog("Ground Control Version " + str(self.data.version) + "\n")
                self.writeToTextConsole("Ground Control " + str(self.data.version) + "\r\n" + message + "\r\n")
                
                #Check that version numbers match
                if float(message[-7:]) < float(self.data.version):
                    self.data.message_queue.put("Message: Warning, your firmware is out of date and may not work correctly with this version of Ground Control\n\n" + "Ground Control Version " + str(self.data.version) + "\r\n" + message)
                if float(message[-7:]) > float(self.data.version):
                    self.data.message_queue.put("Message: Warning, your version of Ground Control is out of date and may not work with this firmware version\n\n" + "Ground Control Version " + str(self.data.version) + "\r\n" + message)
            elif message == "ok\r\n":
                pass #displaying all the 'ok' messages clutters up the display
            else:
                self.writeToTextConsole(message)

    def ondismiss_popup(self, event):
        if global_variables._keyboard:
            global_variables._keyboard.unbind(on_key_down=self.keydown_popup)

    def keydown_popup(self, keyboard, keycode, text, modifiers):
        if (keycode[1] == 'enter') or (keycode[1] =='numpadenter') or (keycode[1] == 'escape'):
            self.dismiss_popup_continue()
        return True     # always swallow keypresses since this is a modal dialog
        
    
    def dismiss_popup_continue(self):
        '''
        
        Close The Pop-up and continue cut
        
        '''
        self._popup.dismiss()
        self.data.quick_queue.put("~") #send cycle resume command to unpause the machine
        self.data.uploadFlag = self.previousUploadStatus #resume cutting if the machine was cutting before
    
    def dismiss_popup_hold(self):
        '''
        
        Close The Pop-up and continue cut
        
        '''
        self._popup.dismiss()
        self.data.uploadFlag = 0 #stop cutting
    
    def setPosOnScreen(self, message):
        '''
        
        This should be moved into the appropriate widget
        
        '''
        
        try:
            startpt = message.find('MPos:') + 5
            
            endpt = message.find('WPos:')
            
            numz  = message[startpt:endpt]
            units = "mm" #message[endpt+1:endpt+3]
            
            valz = numz.split(",")
            
            self.xval  = float(valz[0])
            self.yval  = float(valz[1])
            self.zval  = float(valz[2])
            
            if math.isnan(self.xval):
                self.writeToTextConsole("Unable to resolve x Kinematics.")
                self.xval = 0
            if math.isnan(self.yval):
                self.writeToTextConsole("Unable to resolve y Kinematics.")
                self.yval = 0
            if math.isnan(self.zval):
                self.writeToTextConsole("Unable to resolve z Kinematics.")
                self.zval = 0
            
            self.frontpage.setPosReadout(self.xval,self.yval,self.zval)
            self.frontpage.gcodecanvas.positionIndicator.setPos(self.xval,self.yval,self.data.units)
        except:
            print "One Machine Position Report Command Misread"
            return
    
    def setErrorOnScreen(self, message):
        
        try:
            startpt = message.find(':')+1 
            endpt = message.find(',', startpt)
            leftErrorValueAsString = message[startpt:endpt]
            leftErrorValueAsFloat  = float(leftErrorValueAsString)
            
            startpt = endpt + 1
            endpt = message.find(',', startpt)
            rightErrorValueAsString = message[startpt:endpt]
            
            rightErrorValueAsFloat  = float(rightErrorValueAsString)
            
            if self.data.units == "INCHES":
                rightErrorValueAsFloat = rightErrorValueAsFloat/25.4
                leftErrorValueAsFloat  = leftErrorValueAsFloat/25.4
            
            avgError = (abs(leftErrorValueAsFloat) + abs(rightErrorValueAsFloat))/2
            
            self.frontpage.gcodecanvas.positionIndicator.setError(0, self.data.units)
            self.data.logger.writeErrorValueToLog(avgError)
            
            self.frontpage.gcodecanvas.targetIndicator.setPos(self.xval - .5*rightErrorValueAsFloat + .5*leftErrorValueAsFloat, self.yval - .5*rightErrorValueAsFloat - .5*leftErrorValueAsFloat,self.data.units)
            
            
        except:
            print "Machine Position Report Command Misread Happened Once"
    
if __name__ == '__main__':
    GroundControlApp().run()
