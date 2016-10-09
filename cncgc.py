'''

Kivy Imports

'''
from kivy.app                   import App
from kivy.uix.gridlayout        import GridLayout
from kivy.uix.floatlayout       import FloatLayout
from kivy.uix.anchorlayout      import AnchorLayout
from kivy.core.window           import Window
from kivy.uix.button            import Button
from kivy.clock                 import Clock
from kivy.uix.popup             import Popup


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
    
    json = '''
    [
        {
            "type": "string",
            "title": "Serial Connection",
            "desc": "Select the COM port to connect to machine",
            "section": "Makesmith Settings",
            "key": "COMport"
        },
        {
            "type": "string",
            "title": "X-Axis Pitch",
            "desc": "The number of mm moved per rotation",
            "section": "Makesmith Settings",
            "key": "xPitch"
        },
        {
            "type": "string",
            "title": "Open File",
            "desc": "The path to the open file",
            "section": "Makesmith Settings",
            "key": "openFile"
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
        
        self.data.comport = self.config.get('Makesmith Settings', 'COMport')
        self.data.gcodeFile = self.config.get('Makesmith Settings', 'openFile')
        self.data.config  = self.config
        
        
        '''
        Initializations
        '''
        
        self.frontpage.setUpData(self.data)
        self.nonVisibleWidgets.setUpData(self.data)
        self.frontpage.gcodecanvas.initialzie()
        
        
        '''
        Scheduling
        '''
        
        Clock.schedule_interval(self.runPeriodically, .01)
        
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Makesmith Settings', {'COMport': 'COM5', 'xPitch': 20, 'openFile': " "})

    def build_settings(self, settings):
        """
        Add custom section to the default configuration object.
        """
        settings.add_json_panel('Makesmith Settings', self.config, data=self.json)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        
        if section == "Makesmith Settings":
            if key == "COMport":
                self.data.comport = value
            elif key == 'xPitch':
                print "xPitch changed"

    def close_settings(self, settings):
        """
        Close settings panel
        """
        super(GroundControlApp, self).close_settings(settings)
    
    '''
    
    Update Functions
    
    '''
    
    def runPeriodically(self, *args):
        '''
        this block should be handled within the appropriate widget
        '''
        while not self.data.message_queue.empty(): #if there is new data to be read
            message = self.data.message_queue.get()
            if message[0:2] == "pz":
                self.setPosOnScreen(message)
            elif message[0:2] == "pt":
                self.setTargetOnScreen(message)
            elif message[0:8] == "Message:":
                self.data.uploadFlag = 0
                content = NotificationPopup(cancel = self.dismiss_popup, text = message[9:])
                self._popup = Popup(title="Notification: ", content=content,
                            auto_dismiss=False, size_hint=(0.25, 0.25))
                self._popup.open()
            else:
                try:
                    newText = self.frontpage.consoleText[-3000:] + message
                    self.frontpage.consoleText = newText
                    self.frontpage.textconsole.gotToBottom()  
                except:
                    self.frontpage.consoleText = "text not displayed correctly"
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()
        self.data.uploadFlag = 1
    
    def setPosOnScreen(self, message):
        '''
        
        This should be moved into the appropriate widget
        
        '''
        
        try:
            startpt = message.find('(')
            startpt = startpt + 1
            
            endpt = message.find(')')
            
            numz  = message[startpt:endpt]
            units = message[endpt+1:endpt+3]
            
            valz = numz.split(",")
            
            xval = float(valz[0])
            yval = float(valz[1])
            zval = float(valz[2])
        except:
            print "bad data"
            return
        
        self.frontpage.setPosReadout(xval,yval,zval,units)
        self.frontpage.gcodecanvas.positionIndicator.setPos(xval,yval,self.data.units)
    
    def setTargetOnScreen(self, message):
        '''
        
        This should be moved into the appropriate widget
        
        '''
        try:
            startpt = message.find('(')
            startpt = startpt + 1
            
            endpt = message.find(')')
            
            numz  = message[startpt:endpt]
            units = message[endpt+1:endpt+3]
            
            valz = numz.split(",")
            
            xval = float(valz[0])
            yval = float(valz[1])
            zval = float(valz[2])
            
            self.frontpage.gcodecanvas.targetIndicator.setPos(xval,yval,self.data.units)
        except:
            print "unable to convert to number"
        
    
if __name__ == '__main__':
    GroundControlApp().run()
