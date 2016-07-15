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
'''

Main UI Program

'''

class GroundControlApp(App):
    
    json = '''
    [
        {
            "type": "string",
            "title": "Serial Connection",
            "desc": "Sellect the COM port to connect to machine",
            "section": "Makesmith Settings",
            "key": "COMport"
        },
        {
            "type": "string",
            "title": "X-Axis Pitch",
            "desc": "The number of mm moved per rotation",
            "section": "Makesmith Settings",
            "key": "xPitch"
        }
    ]
    '''
    
    def build(self):
        interface       =  FloatLayout()
        self.data       =  Data()
        
        
        self.frontpage = FrontPage(name='FrontPage')
        interface.add_widget(self.frontpage)
        
        self.nonVisibleWidgets = NonVisibleWidgets()
        
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
        
        
        '''
        Load User Settings
        '''
        self.data.comport = self.config.get('Makesmith Settings', 'COMport')
        self.data.config  = self.config
        
        
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Makesmith Settings', {'COMport': 'COM5', 'xPitch': 20})

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
        if not self.data.message_queue.empty(): #if there is new data to be read
            message = self.data.message_queue.get()
            if message[0:2] == "pz":
                self.setPosOnScreen(message)
            elif message[0:6] == "gready":
                self.frontpage.gcodecanvas.readyFlag = 1
                if self.frontpage.gcodecanvas.uploadFlag == 1:
                    self.frontpage.sendLine()
                    self.frontpage.gcodecanvas.readyFlag = 0
            else:
                self.frontpage.textconsole.gotToBottom()
                try:
                    newText = self.frontpage.consoleText[-3000:] + message
                    self.frontpage.consoleText = newText
                    
                except:
                    self.frontpage.consoleText = "text not displayed correctly"
    
    def setPosOnScreen(self, message):
        '''
        
        This should be moved into the appropriate widget
        
        '''
        
        startpt = message.find('(')
        startpt = startpt + 1
        
        endpt = message.find(')')
        
        numz = message[startpt:endpt]
        
        valz = numz.split(",")
        
        xval = -1*float(valz[0])*1.27
        yval = float(valz[1])*1.27
        zval = float(valz[2])*1.27
    
        self.frontpage.setPosReadout(xval,yval,zval)
        self.frontpage.gcodecanvas.setCrossPos(xval,yval)
        
    
if __name__ == '__main__':
    GroundControlApp().run()
