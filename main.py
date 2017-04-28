'''

Kivy Imports

'''
from kivy.config                import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
from kivy.app                   import App
from kivy.uix.gridlayout        import GridLayout
from kivy.uix.floatlayout       import FloatLayout
from kivy.uix.anchorlayout      import AnchorLayout
from kivy.core.window           import Window
from kivy.uix.button            import Button
from kivy.clock                 import Clock
from kivy.uix.popup             import Popup
import math


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
        }
    ]
    '''
    
    gcsettings = '''
    [
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
        
        self.data.comport = self.config.get('Maslow Settings', 'COMport')
        self.data.gcodeFile = self.config.get('Maslow Settings', 'openFile')
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
        self.push_settings_to_machine()
        self.data.bind(connectionStatus = self.push_settings_to_machine)
        
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the config sections.
        """
        config.setdefaults('Maslow Settings', {'COMport': '',
                                               'zAxis': 0, 
                                               'zDistPerRot':3.17, 
                                               'bedWidth':2438.4, 
                                               'bedHeight':1219.2, 
                                               'motorOffsetY':463, 
                                               'motorSpacingX':2978.4, 
                                               'sledWidth':310, 
                                               'sledHeight':139, 
                                               'sledCG':79, 
                                               'openFile': " "})

        config.setdefaults('Advanced Settings', {'encoderSteps': 8148.0,
                                                 'gearTeeth': 10, 
                                                 'chainPitch':6.35,
                                                 'zEncoderSteps':7560.0})
        
        config.setdefaults('Ground Control Settings', {'zoomIn': "pageup",
                                                 'validExtensions':".nc, .ngc, .text, .gcode",
                                                 'zoomOut': "pagedown"})

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
            if key == "COMport":
                self.data.comport = value
            self.push_settings_to_machine()

            if (key == "bedHeight" or key == "bedWidth"):
                self.frontpage.gcodecanvas.drawWorkspace()

    def close_settings(self, settings):
        """
        Close settings panel
        """
        super(GroundControlApp, self).close_settings(settings)
    
    def push_settings_to_machine(self, *args):
        
        cmdString = ("B03" 
            +" A" + str(self.data.config.get('Maslow Settings', 'bedWidth'))
            +" C" + str(self.data.config.get('Maslow Settings', 'bedHeight'))
            +" Q" + str(self.data.config.get('Maslow Settings', 'motorSpacingX'))
            +" E" + str(self.data.config.get('Maslow Settings', 'motorOffsetY'))
            +" F" + str(self.data.config.get('Maslow Settings', 'sledWidth'))
            +" R" + str(self.data.config.get('Maslow Settings', 'sledHeight'))
            +" H" + str(self.data.config.get('Maslow Settings', 'sledCG'))
            +" I" + str(self.data.config.get('Maslow Settings', 'zAxis'))
            +" J" + str(self.data.config.get('Advanced Settings', 'encoderSteps'))
            +" K" + str(self.data.config.get('Advanced Settings', 'gearTeeth'))
            +" M" + str(self.data.config.get('Advanced Settings', 'chainPitch'))
            +" N" + str(self.data.config.get('Maslow Settings'  , 'zDistPerRot'))
            +" P" + str(self.data.config.get('Advanced Settings', 'zEncoderSteps'))
            + " "
        )
        
        self.data.gcode_queue.put(cmdString)
    
    '''
    
    Update Functions
    
    '''
    
    def writeToTextConsole(self, message):
        try:
            newText = self.frontpage.consoleText[-3000:] + message
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
                if message[1:10] == "PosError:":
                    self.setErrorOnScreen(message)
            elif message[0:8] == "Message:":
                self.previousUploadStatus = self.data.uploadFlag 
                self.data.uploadFlag = 0
                content = NotificationPopup(continueOn = self.dismiss_popup_continue, hold=self.dismiss_popup_hold , text = message[9:])
                self._popup = Popup(title="Notification: ", content=content,
                            auto_dismiss=False, size_hint=(0.35, 0.35))
                self._popup.open()
            else:
                self.writeToTextConsole(message)
    
    def dismiss_popup_continue(self):
        '''
        
        Close The Pop-up and continue cut
        
        '''
        self._popup.dismiss()
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
            
            xval  = float(valz[0])
            yval  = float(valz[1])
            zval  = float(valz[2])
            
            if math.isnan(xval):
                self.writeToTextConsole("Unable to resolve x Kinematics.")
                xval = 0
            if math.isnan(yval):
                self.writeToTextConsole("Unable to resolve y Kinematics.")
                yval = 0
            if math.isnan(zval):
                self.writeToTextConsole("Unable to resolve z Kinematics.")
                zval = 0
        except:
            print "bad data"
            return
        
        self.frontpage.setPosReadout(xval,yval,zval)
        self.frontpage.gcodecanvas.positionIndicator.setPos(xval,yval,self.data.units)
    
    def setErrorOnScreen(self, message):
        
        try:
            startpt = message.find(':')+1 
            endpt = message.find(',', startpt)
            errorValueAsString = message[startpt:endpt]
            errorValueAsFloat  = float(errorValueAsString)
            
            self.frontpage.gcodecanvas.positionIndicator.setError(errorValueAsFloat)
            self.data.logger.writeErrorValueToLog(errorValueAsFloat)
        except:
            print "unable to read error value"
        
        
    
if __name__ == '__main__':
    GroundControlApp().run()
