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
            "desc": "The horizontal distance between the center of the motor shafts in MM.",
            "section": "Maslow Settings",
            "key": "motorSpacingX"
            
        },
        {
            "type": "string",
            "title": "Work Area Width in MM",
            "desc": "The width of the machine working area (normally 8 feet).",
            "section": "Maslow Settings",
            "key": "bedWidth"
        },
        {
            "type": "string",
            "title": "Work Area Height in MM",
            "desc": "The Height of the machine working area (normally 4 feet).",
            "section": "Maslow Settings",
            "key": "bedHeight"
        },
        {
            "type": "string",
            "title": "Motor Offset Height in MM",
            "desc": "The vertical distance from the edge of the work area to the level of the motors.",
            "section": "Maslow Settings",
            "key": "motorOffsetY"
        },
        {
            "type": "string",
            "title": "Distance Between Sled Mounting Points",
            "desc": "The horizontal distance between the points where the chains mount to the sled.",
            "section": "Maslow Settings",
            "key": "sledWidth"
        },
        {
            "type": "string",
            "title": "Vertical Distance Sled Mounts to Cutter",
            "desc": "The vertical distance between where the chains mount on the sled to the cutting tool.",
            "section": "Maslow Settings",
            "key": "sledHeight"
        },
        {
            "type": "string",
            "title": "Center Of Gravity",
            "desc": "How far below the cutting bit is the center of gravity. This can be found by resting the sled on a round object and observing where it balances.",
            "section": "Maslow Settings",
            "key": "sledCG"
        },
        {
            "type": "bool",
            "title": "z-axis installed",
            "desc": "Does the machine have an automatic z-axis?",
            "section": "Maslow Settings",
            "key": "zAxis"
        },
        {
            "type": "string",
            "title": "Z-Axis Pitch",
            "desc": "The number of mm moved per rotation of the z-axis",
            "section": "Maslow Settings",
            "key": "zDistPerRot"
        },
        {
            "type": "string",
            "title": "Open File",
            "desc": "The path to the open file",
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
            "title": "Macro 2",
            "desc": "User defined gcode bound to the Macro 2 button",
            "section": "Maslow Settings",
            "key": "macro2"
        }
    ]
    '''

    advanced = '''
    [
        {
            "type": "string",
            "title": "Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the left or right motor",
            "section": "Advanced Settings",
            "key": "encoderSteps"
        },
        {
            "type": "string",
            "title": "Gear Teeth",
            "desc": "The number of teeth on the gear of the left or right motor",
            "section": "Advanced Settings",
            "key": "gearTeeth"
        },
        {
            "type": "string",
            "title": "Chain Pitch",
            "desc": "The distance between chain roller centers",
            "section": "Advanced Settings",
            "key": "chainPitch"
        },
        {
            "type": "string",
            "title": "Z-Axis Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the z-axis",
            "section": "Advanced Settings",
            "key": "zEncoderSteps"
        },
        {
            "type": "string",
            "title": "Home Position X Coordinate",
            "desc": "The X coordinate of the home position",
            "section": "Advanced Settings",
            "key": "homeX"
        },
        {
            "type": "string",
            "title": "Home Position Y Coordinate",
            "desc": "The X coordinate of the home position",
            "section": "Advanced Settings",
            "key": "homeY"
        },
        {
            "type": "bool",
            "title": "Truncate Floating Point Numbers",
            "desc": "Truncate floating point numbers at the specified number of decimal places",
            "section": "Advanced Settings",
            "key": "truncate"
        },
        {
            "type": "string",
            "title": "Floating Point Precision",
            "desc": "If truncate floating point numbers is enabled, the number of digits after the decimal place to preserve",
            "section": "Advanced Settings",
            "key": "digits"
        },
        {
            "type": "options",
            "title": "Kinematics Type",
            "desc": "Switch between trapezoidal and triangular kinematics",
            "options": ["Quadrilateral", "Triangular"],
            "section": "Advanced Settings",
            "key": "kinematicsType"
        },
        {
            "type": "string",
            "title": "Rotation Radius for Triangular Kinematics",
            "desc": "The distance between where the chains attach and the center of the router bit in mm",
            "section": "Advanced Settings",
            "key": "rotationRadius"
        },
        {
            "type": "bool",
            "title": "Enable Custom Positional PID Values",
            "desc": "Enable using custom values for the positional PID controller. Turning this off will return to the default values",
            "section": "Advanced Settings",
            "key": "enablePosPIDValues"
        },
        {
            "type": "string",
            "title": "Kp Position",
            "desc": "The proportional constant for the position PID controller",
            "section": "Advanced Settings",
            "key": "KpPos"
        },
        {
            "type": "string",
            "title": "Ki Position",
            "desc": "The integral constant for the position PID controller",
            "section": "Advanced Settings",
            "key": "KiPos"
        },
        {
            "type": "string",
            "title": "Kd Position",
            "desc": "The derivative constant for the position PID controller",
            "section": "Advanced Settings",
            "key": "KdPos"
        },
        {
            "type": "string",
            "title": "Proportional Weighting",
            "desc": "The ratio of Proportional on Error (1) to Proportional on Measure (0)",
            "section": "Advanced Settings",
            "key": "propWeight"
        },
        {
            "type": "bool",
            "title": "Enable Custom Velocity PID Values",
            "desc": "Enable using custom values for the Velocity PID controller. Turning this off will return to the default values",
            "section": "Advanced Settings",
            "key": "enableVPIDValues"
        },
        {
            "type": "string",
            "title": "Kp Velocity",
            "desc": "The proportional constant for the velocity PID controller",
            "section": "Advanced Settings",
            "key": "KpV"
        },
        {
            "type": "string",
            "title": "Ki Velocity",
            "desc": "The integral constant for the velocity PID controller",
            "section": "Advanced Settings",
            "key": "KiV"
        },
        {
            "type": "string",
            "title": "Kd Velocity",
            "desc": "The derivative constant for the velocity PID controller",
            "section": "Advanced Settings",
            "key": "KdV"
        }
    ]
    '''
    
    gcsettings = '''
    [
        {
            "type": "bool",
            "title": "Center Canvas on Window Resize",
            "desc": "When resizing the window, automatically reset the Gcode canvas to be centered and zoomed out. Program must be restarted to take effect.",
            "section": "Ground Control Settings",
            "key": "centerCanvasOnResize"
        },
        {
            "type": "string",
            "title": "Zoom In",
            "desc": "Pressing this key will zoom in. Note combinations of keys like \'shift\' + \'=\' may not work as expected. Program must be restarted to take effect.",
            "section": "Ground Control Settings",
            "key": "zoomIn"
        },
        {
            "type": "string",
            "title": "Zoom Out",
            "desc": "Pressing this key will zoom in. Note combinations of keys like \'shift\' + \'=\' may not work as expected. Program must be restarted to take effect.",
            "section": "Ground Control Settings",
            "key": "zoomOut"
        },
        {
            "type": "string",
            "title": "Valid File Extensions",
            "desc": "Valid file extensions for Ground Control to open. Comma separated list.",
            "section": "Ground Control Settings",
            "disabled": "True",
            "key": "validExtensions"
        }
    ]
    '''
    
    def build(self):
        Window.maximize()
        
        interface       =  FloatLayout()
        self.data       =  Data()
        
        self.frontpage = FrontPage(self.data, name='FrontPage')
        interface.add_widget(self.frontpage)
        
        self.nonVisibleWidgets = NonVisibleWidgets()
        
        
        '''
        Load User Settings
        '''
        
        self.config.set('Advanced Settings', 'truncate', 0)
        self.config.set('Advanced Settings', 'digits', 4)
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
        config.setdefaults('Maslow Settings', {'COMport'         : '',
                                                 'zAxis'         : 0, 
                                                 'zDistPerRot'   : 3.17, 
                                                 'bedWidth'      : 2438.4, 
                                                 'bedHeight'     : 1219.2, 
                                                 'motorOffsetY'  : 463, 
                                                 'motorSpacingX' : 2978.4, 
                                                 'sledWidth'     : 310, 
                                                 'sledHeight'    : 139, 
                                                 'sledCG'        : 79, 
                                                 'openFile'      : " ",
                                                 'macro1'        : "",
                                                 'macro2'        : ""})

        config.setdefaults('Advanced Settings', {'encoderSteps'       : 8148.0,
                                                 'gearTeeth'          : 10, 
                                                 'chainPitch'         : 6.35,
                                                 'zEncoderSteps'      : 7560.0,
                                                 'homeX'              : 0.0,
                                                 'homeY'              : 0.0,
                                                 'truncate'           : 0,
                                                 'digits'             : 4,
                                                 'kinematicsType'     : 'Quadrilateral',
                                                 'rotationRadius'     : '100',
                                                 'enablePosPIDValues' : 0,
                                                 'KpPos'              : 400,
                                                 'KiPos'              : 5,
                                                 'KdPos'              : 10,
                                                 'propWeight'         : 1,
                                                 'enableVPIDValues'   : 0,
                                                 'KpV'                : 20,
                                                 'KiV'                : 1,
                                                 'KdV'                : 0})
        
        config.setdefaults('Ground Control Settings', {'centerCanvasOnResize': 0,
                                                 'zoomIn': "pageup",
                                                 'zoomOut': "pagedown",
                                                 'validExtensions': ".nc, .ngc, .text, .gcode"})

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
            KpPos = 400
            KiPos = 5
            KdPos = 10
            propWeight = 1
        
        if int(self.data.config.get('Advanced Settings', 'enableVPIDValues')) == 1:
            KpV = float(self.data.config.get('Advanced Settings', 'KpV'))
            KiV = float(self.data.config.get('Advanced Settings', 'KiV'))
            KdV = float(self.data.config.get('Advanced Settings', 'KdV'))
        else:
            KpV = 20
            KiV = 1
            KdV = 0
        
        
        
        cmdString = ("B12" 
            +" I" + str(self.data.config.get('Maslow Settings', 'zAxis'))
            +" J" + str(self.data.config.get('Advanced Settings', 'encoderSteps'))
            +" K" + str(self.data.config.get('Advanced Settings', 'gearTeeth'))
            +" M" + str(self.data.config.get('Advanced Settings', 'chainPitch'))
            +" N" + str(self.data.config.get('Maslow Settings'  , 'zDistPerRot'))
            +" P" + str(self.data.config.get('Advanced Settings', 'zEncoderSteps'))
            +" R" + str(propWeight)
            +" S" + str(KpPos)
            +" T" + str(KiPos)
            +" U" + str(KdPos)
            +" V" + str(KpV)
            +" W" + str(KiV)
            +" X" + str(KdV)
            + " "
        )
        
        self.data.gcode_queue.put(cmdString)
        
        #Push kinematics settings to machine
        if self.data.config.get('Advanced Settings', 'kinematicsType') == 'Quadrilateral':
            kinematicsType = 1
        else:
            kinematicsType = 2
        
        cmdString = ("B03" 
            +" A" + str(self.data.config.get('Maslow Settings', 'bedWidth'))
            +" C" + str(self.data.config.get('Maslow Settings', 'bedHeight'))
            +" Q" + str(self.data.config.get('Maslow Settings', 'motorSpacingX'))
            +" E" + str(self.data.config.get('Maslow Settings', 'motorOffsetY'))
            +" F" + str(self.data.config.get('Maslow Settings', 'sledWidth'))
            +" R" + str(self.data.config.get('Maslow Settings', 'sledHeight'))
            +" H" + str(self.data.config.get('Maslow Settings', 'sledCG'))
            +" Y" + str(kinematicsType)
            +" Z" + str(self.data.config.get('Advanced Settings', 'rotationRadius'))
            + " "
        )
        
        self.data.gcode_queue.put(cmdString)
        
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
            
            self.data.logger.writeToLog(message)
            
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
                self._popup = Popup(title="Notification: ", content=content,
                            auto_dismiss=False, size=(360,240), size_hint=(None, None))
                self._popup.open()
                if global_variables._keyboard:
                    global_variables._keyboard.bind(on_key_down=self.keydown_popup)
                    self._popup.bind(on_dismiss=self.ondismiss_popup)
            elif message[0:8] == "Firmware":
                self.data.logger.writeToLog("Ground Control Version " + str(self.data.version) + "\n")
                self.writeToTextConsole("Ground Control " + str(self.data.version) + "\r\n" + message + "\r\n")
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
