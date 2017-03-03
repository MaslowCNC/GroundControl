'''

Kivy Imports

'''
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
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
            "section": "Maslow Settings",
            "key": "COMport"
        },
        {
            "type": "string",
            "title": "Z-Axis Pitch",
            "desc": "The number of mm moved per rotation of the z-axis",
            "section": "Maslow Settings",
            "key": "zPitch"
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
            "desc": "The vertical distance from the corner of the work area to the motor.",
            "section": "Maslow Settings",
            "key": "motorOffsetY"
        },
        {
            "type": "string",
            "title": "Motor Offset Horizontal in MM",
            "desc": "The horizontal distance from the corner of the work area to the motor.",
            "section": "Maslow Settings",
            "key": "motorOffsetX"
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
            "type": "string",
            "title": "Open File",
            "desc": "The path to the open file",
            "section": "Maslow Settings",
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
        
        
        return interface
        
    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Maslow Settings', {'COMport': '',
                                               'zPitch': 20,
                                               'zAxis': False, 
                                               'bedWidth':2438.4, 
                                               'bedHeight':1219.2, 
                                               'motorOffsetY':100, 
                                               'motorOffsetX':100, 
                                               'sledWidth':100, 
                                               'sledHeight':100, 
                                               'sledCG':100, 
                                               'openFile': " "})

    def build_settings(self, settings):
        """
        Add custom section to the default configuration object.
        """
        settings.add_json_panel('Maslow Settings', self.config, data=self.json)

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        
        if section == "Makesmith Settings":
            print "this is where it should push to machine"
            if key == "COMport":
                self.data.comport = value
            elif key == 'zPitch':
                print "zPitch changed"

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
