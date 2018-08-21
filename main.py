'''

Kivy Imports

'''
from kivy.config                import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('graphics', 'minimum_width', '620')
Config.set('graphics', 'minimum_height', '440')
Config.set('kivy', 'exit_on_escape', '0')
Config.set('graphics', 'multisamples', '0')
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
import re
import json

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
from Settings                     import   maslowSettings
from UIElements.backgroundMenu    import   BackgroundMenu
'''

Main UI Program

'''

class GroundControlApp(App):

    def get_application_config(self):
        return super(GroundControlApp, self).get_application_config(
            '~/%(appname)s.ini')
    
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
        elif self.config.get('Maslow Settings', 'colorScheme') == 'DarkGreyBlue':
            self.data.iconPath               = './Images/Icons/darkgreyblue/'
            self.data.fontColor              = '[color=000000]'
            self.data.drawingColor           = [1,1,1]
            Window.clearcolor                = (0.06, 0.10, 0.2, 1)
            self.data.posIndicatorColor      =  [0.51,0.93,0.97]
            self.data.targetInicatorColor = [1,0,0]

        
        
        Window.maximize()
        
        
        self.frontpage = FrontPage(self.data, name='FrontPage')
        interface.add_widget(self.frontpage)
        
        self.nonVisibleWidgets = NonVisibleWidgets()
        
        
        '''
        Load User Settings
        '''
        
        # force create an ini no matter what.
        self.config.write()

        if self.config.get('Advanced Settings', 'encoderSteps') == '8148.0':
            self.data.message_queue.put("Message: This update will adjust the the number of encoder pulses per rotation from 8,148 to 8,113 in your settings which improves the positional accuracy.\n\nPerforming a calibration will help you get the most out of this update.")
            self.config.set('Advanced Settings', 'encoderSteps', '8113.73')
        #up the maximum feedrate
        if self.config.get('Advanced Settings', 'maxFeedrate') == '700':
            self.data.message_queue.put("Message: This update will increase the maximum feedrate of your machine. You can adjust this value under the Advanced settings.")
            self.config.set('Advanced Settings', 'maxFeedrate', '800')
            self.config.write()
        
        self.data.comport = self.config.get('Maslow Settings', 'COMport')
        self.data.gcodeFile = self.config.get('Maslow Settings', 'openFile')
        offsetX = float(self.config.get('Advanced Settings', 'homeX'))
        offsetY = float(self.config.get('Advanced Settings', 'homeY'))
        self.data.gcodeShift = [offsetX,offsetY]
        self.data.config  = self.config
        self.config.add_callback(self.configSettingChange)

        # Background image setup
        self.data.backgroundFile = self.config.get('Background Settings',
                                                   'backgroundFile')
        self.data.backgroundManualReg = json.loads(
                        self.config.get('Background Settings', 'manualReg'))
        if self.data.backgroundFile != "":
            BackgroundMenu(self.data).processBackground()
        
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
        self.data.bind(connectionStatus = self.requestMachineSettings)
        self.data.pushSettings = self.requestMachineSettings
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the config sections.
        """
        # Calculate computed settings on load
        config.add_callback(self.computeSettings)
        config.setdefaults('Computed Settings', maslowSettings.getDefaultValueSection('Computed Settings'))
        config.setdefaults('Maslow Settings', maslowSettings.getDefaultValueSection('Maslow Settings'))
        config.setdefaults('Advanced Settings', maslowSettings.getDefaultValueSection('Advanced Settings'))
        config.setdefaults('Ground Control Settings', maslowSettings.getDefaultValueSection('Ground Control Settings'))
        config.setdefaults('Background Settings', maslowSettings.getDefaultValueSection('Background Settings'))
        config.remove_callback(self.computeSettings)
        
    def build_settings(self, settings):
        """
        Add custom section to the default configuration object.
        """
        
        settings.add_json_panel('Maslow Settings', self.config, data=maslowSettings.getJSONSettingSection('Maslow Settings'))
        settings.add_json_panel('Advanced Settings', self.config, data=maslowSettings.getJSONSettingSection('Advanced Settings'))
        settings.add_json_panel('Ground Control Settings', self.config, data=maslowSettings.getJSONSettingSection("Ground Control Settings"))
        

    def computeSettings(self, section, key, value):
        # Update Computed settings
        if key == 'kinematicsType':
            if value == 'Quadrilateral':
                self.config.set('Computed Settings', 'kinematicsTypeComputed', "1")
            else:
                self.config.set('Computed Settings', 'kinematicsTypeComputed', "2")

        elif (key == 'gearTeeth' or key == 'chainPitch') and self.config.has_option('Advanced Settings', 'gearTeeth') and self.config.has_option('Advanced Settings', 'chainPitch'):
            distPerRot = float(self.config.get('Advanced Settings', 'gearTeeth')) * float(self.config.get('Advanced Settings', 'chainPitch'))
            self.config.set('Computed Settings', "distPerRot", str(distPerRot))

            if self.config.has_option('Advanced Settings', 'leftChainTolerance'):
                distPerRotLeftChainTolerance = (1 + (float(self.config.get('Advanced Settings', 'leftChainTolerance')) / 100)) * float(self.config.get('Advanced Settings', 'gearTeeth')) * float(self.config.get('Advanced Settings', 'chainPitch'))
                self.config.set('Computed Settings', "distPerRotLeftChainTolerance", str("{0:.5f}".format(distPerRotLeftChainTolerance)))
            if self.config.has_option('Advanced Settings', 'rightChainTolerance'):
                distPerRotRightChainTolerance = (1 + (float(self.config.get('Advanced Settings', 'rightChainTolerance')) / 100)) * float(self.config.get('Advanced Settings', 'gearTeeth')) * float(self.config.get('Advanced Settings', 'chainPitch'))
                self.config.set('Computed Settings', "distPerRotRightChainTolerance", str("{0:.5f}".format(distPerRotRightChainTolerance)))
        
        elif key == 'leftChainTolerance' and self.config.has_option('Advanced Settings', 'leftChainTolerance') and self.config.has_option('Computed Settings', 'distPerRot'):
            distPerRotLeftChainTolerance = (1 + (float(self.config.get('Advanced Settings', 'leftChainTolerance')) / 100)) * float(self.config.get('Computed Settings', 'distPerRot'))
            self.config.set('Computed Settings', "distPerRotLeftChainTolerance", str("{0:.5f}".format(distPerRotLeftChainTolerance)))
        
        elif key == 'rightChainTolerance' and self.config.has_option('Advanced Settings', 'rightChainTolerance') and self.config.has_option('Computed Settings', 'distPerRot'):
            distPerRotRightChainTolerance = (1 + (float(self.config.get('Advanced Settings', 'rightChainTolerance')) / 100)) * float(self.config.get('Computed Settings', 'distPerRot'))
            self.config.set('Computed Settings', "distPerRotRightChainTolerance", str("{0:.5f}".format(distPerRotRightChainTolerance)))
        
        elif key == 'enablePosPIDValues':
            for key in ('KpPos', 'KiPos', 'KdPos', 'propWeight'):
                if int(self.config.get('Advanced Settings', 'enablePosPIDValues')) == 1:
                    value = float(self.config.get('Advanced Settings', key))
                else:
                    value = maslowSettings.getDefaultValue('Advanced Settings', key)
                self.config.set('Computed Settings', key + "Main", value)
            #updated computed values for z-axis
            for key in ('KpPosZ', 'KiPosZ', 'KdPosZ', 'propWeightZ'):
                if int(self.config.get('Advanced Settings', 'enablePosPIDValues')) == 1:
                    value = float(self.config.get('Advanced Settings', key))
                else:
                    value = maslowSettings.getDefaultValue('Advanced Settings', key)
                self.config.set('Computed Settings', key, value)

        elif key == 'enableVPIDValues':
            for key in ('KpV', 'KiV', 'KdV'):
                if int(self.config.get('Advanced Settings', 'enablePosPIDValues')) == 1:
                    value = float(self.config.get('Advanced Settings', key))
                else:
                    value = maslowSettings.getDefaultValue('Advanced Settings', key)
                self.config.set('Computed Settings', key + "Main", value)
            #updated computed values for z-axis
            for key in ('KpVZ', 'KiVZ', 'KdVZ'):
                if int(self.config.get('Advanced Settings', 'enablePosPIDValues')) == 1:
                    value = float(self.config.get('Advanced Settings', key))
                else:
                    value = maslowSettings.getDefaultValue('Advanced Settings', key)
                self.config.set('Computed Settings', key, value)
        
        elif key == 'chainOverSprocket':
            if value == 'Top':
                self.config.set('Computed Settings',  'chainOverSprocketComputed', 1)
            else:
                self.config.set('Computed Settings',  'chainOverSprocketComputed', 2)

        elif key == 'fPWM':
            if value == '31,000Hz':
                self.config.set('Computed Settings',  'fPWMComputed', 1)
            elif value == '4,100Hz':
                self.config.set('Computed Settings',  'fPWMComputed', 2)
            else: 
                self.config.set('Computed Settings',  'fPWMComputed', 3)

    def configSettingChange(self, section, key, value):
        """
        
        Respond to changes in the configuration.
        
        """
        
        # Update GC things
        if section == "Maslow Settings":
            if key == "COMport":
                self.data.comport = value
            
            if (key == "bedHeight" or key == "bedWidth"):
                self.frontpage.gcodecanvas.drawWorkspace()

            if (key == "macro1_title") or (key == "macro2_title"):
                self.frontpage.update_macro_titles()

        if section == "Advanced Settings":
            if (key == "truncate") or (key == "digits"):
                self.frontpage.gcodecanvas.reloadGcode()
            if (key == "spindleAutomate"):
                if (value == "Servo"):
                    value = 1
                elif (value == "Relay_High"):
                    value = 2
                elif (value == "Relay_Low"):
                    value = 3
                else:
                    value = 0
    
        
        # Update Computed Settings
        self.computeSettings(section, key, value)
        
        # Write the settings change to the Disk
        self.data.config.write()

        # only run on live connection
        if self.data.connectionStatus != 1:
            return
        
        # Push settings that can be directly written to machine
        firmwareKey = maslowSettings.getFirmwareKey(section, key)
        if firmwareKey is not None:
            self.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(value))
    
    def requestMachineSettings(self, *args):
        ''' 
        Requests the machine to report all settings.  This will implicitly
        cause a sync of the machine settings because if GroundControl sees a
        reported setting which does match its expected value, GC will push the
        correct setting to the machine.
        '''
        if self.data.connectionStatus == 1:
            self.data.gcode_queue.put("$$")
    
    def receivedSetting(self, message):
        '''
        This parses a settings report from the machine, usually received in 
        response to a $$ request.  If the value received does not match the 
        expected value.
        '''
        parameter, position = self.parseFloat(message, 0)
        value, position = self.parseFloat(message, position)
        if (parameter is not None and value is not None):
            maslowSettings.syncFirmwareKey(int(parameter), value, self.data)
    
    def parseFloat(self, text, position=0):
        '''
        Takes a string and parses out the float found at position default to 0
        returning a list of the matched float and the ending
        position of the float
        '''
        # This regex comes from a python docs recommended 
        regex = re.compile("[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")
        match = regex.search(text[position:])
        if match:
            return (float(match.group(0)), match.end(0))
        else:
            return (None, position)
    
    '''
    
    Update Functions
    
    '''
    
    def writeToTextConsole(self, message):
        try:
            newText = self.frontpage.consoleText[-2000:] + message
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
            elif message[0] == "$":
                self.receivedSetting(message)
            elif message[0] == "[":
                if message[1:4] == "PE:":
                    self.setErrorOnScreen(message)
                elif message[1:8] == "Measure":
                    measuredDist = float(message[9:len(message)-3])
                    try:
                        self.data.measureRequest(measuredDist)
                    except:
                        print "No function has requested a measurement"
            elif message[0:13] == "Maslow Paused":
                self.data.uploadFlag = 0
                self.writeToTextConsole(message)
            elif message[0:8] == "Message:":
                if self.data.calibrationInProcess and message[0:15] == "Message: Unable":   #this suppresses the annoying messages about invalid chain lengths during the calibration process
                    break
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
            elif message[0:6] == "ALARM:":
                self.previousUploadStatus = self.data.uploadFlag 
                self.data.uploadFlag = 0
                try:
                    self._popup.dismiss()                                           #close any open popup
                except:
                    pass                                                            #there wasn't a popup to close
                content = NotificationPopup(continueOn = self.dismiss_popup_continue, text = message[7:])
                if sys.platform.startswith('darwin'):
                    self._popup = Popup(title="Alarm Notification: ", content=content,
                            auto_dismiss=False, size=(360,240), size_hint=(.3, .3))
                else:
                    self._popup = Popup(title="Alarm Notification: ", content=content,
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
        except:
            print "One Machine Position Report Command Misread"
            return

        self.frontpage.setPosReadout(self.xval, self.yval, self.zval)
        self.frontpage.gcodecanvas.positionIndicator.setPos(self.xval,self.yval,self.data.units)
    
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
