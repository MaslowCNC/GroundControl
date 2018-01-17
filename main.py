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
from Settings                     import   maslowSettings
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
        config.setdefaults('Maslow Settings', maslowSettings.getDefaultValueSection('Maslow Settings'))
        config.setdefaults('Advanced Settings', maslowSettings.getDefaultValueSection('Advanced Settings'))
        config.setdefaults('Ground Control Settings', maslowSettings.getDefaultValueSection('Ground Control Settings'))

    def build_settings(self, settings):
        """
        Add custom section to the default configuration object.
        """
        settings.add_json_panel('Maslow Settings', self.config, data=maslowSettings.getJSONSettingSection('Maslow Settings'))
        settings.add_json_panel('Advanced Settings', self.config, data=maslowSettings.getJSONSettingSection('Advanced Settings'))
        settings.add_json_panel('Ground Control Settings', self.config, data=maslowSettings.getJSONSettingSection("Ground Control Settings"))
        self.config.add_callback(self.configSettingChange)

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
        
        # only run on live connection
        if self.data.connectionStatus != 1:
            return
        
        # Push settings that can be directly written to machine
        firmwareKey = maslowSettings.getFirmwareKey(section, key)
        if firmwareKey is not None:
            self.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(value))
        
        #Push Settings that require some calculations
        elif key == 'kinematicsType':
            if value == 'Quadrilateral':
                kinematicsType = 1
            else:
                kinematicsType = 2
            self.data.gcode_queue.put("$7=" + str(kinematicsType))

        elif key == 'gearTeeth' or key == 'chainPitch':
            distPerRot = float(self.data.config.get('Advanced Settings', 'gearTeeth')) * float(self.data.config.get('Advanced Settings', 'chainPitch'))
            self.data.gcode_queue.put("$13=" + str(distPerRot))
        
        elif key in ('KpPos', 'KiPos', 'KdPos', 'propWeight'):
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
            if key == 'KpPos':
                self.data.gcode_queue.put("$21=" + str(KpPos))
                self.data.gcode_queue.put("$29=" + str(KpPos))
            elif key == 'KiPos':
                self.data.gcode_queue.put("$22=" + str(KiPos))
                self.data.gcode_queue.put("$30=" + str(KiPos))
            elif key == 'KdPos':
                self.data.gcode_queue.put("$23=" + str(KdPos))
                self.data.gcode_queue.put("$31=" + str(KdPos))
            elif key == 'propWeight':
                self.data.gcode_queue.put("$24=" + str(propWeight))
                self.data.gcode_queue.put("$32=" + str(propWeight))

        elif key in ('KpV', 'KiV', 'KdV'):
            if int(self.data.config.get('Advanced Settings', 'enableVPIDValues')) == 1:
                KpV = float(self.data.config.get('Advanced Settings', 'KpV'))
                KiV = float(self.data.config.get('Advanced Settings', 'KiV'))
                KdV = float(self.data.config.get('Advanced Settings', 'KdV'))
            else:
                KpV = 7
                KiV = 0
                KdV = .28
            if key == 'KpV':
                self.data.gcode_queue.put("$25=" + str(KpV))
                self.data.gcode_queue.put("$33=" + str(KpV))
            elif key =='KiV':
                self.data.gcode_queue.put("$26=" + str(KiV))
                self.data.gcode_queue.put("$34=" + str(KiV))
            elif key == 'KdV':
                self.data.gcode_queue.put("$27=" + str(KdV))
                self.data.gcode_queue.put("$35=" + str(KdV))
    
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
            KpV = 5
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
        self.data.gcode_queue.put("$37=" + str(self.data.config.get('Advanced Settings', 'chainSagCorrection')))


        
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
