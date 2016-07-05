'''

Kivy Imports

'''
from kivy.app                   import App
from kivy.uix.floatlayout       import FloatLayout
from kivy.uix.gridlayout        import GridLayout
from kivy.uix.anchorlayout      import AnchorLayout
from kivy.core.window           import Window
from kivy.uix.button            import Button
from kivy.clock                 import Clock
from kivy.uix.screenmanager     import ScreenManager, Screen, SlideTransition

'''

Other Imports

'''

import Queue

'''

Internal Module Imports

'''

from UIElements.frontPage        import   FrontPage
from UIElements.gcodeCanvas      import   GcodeCanvas
from UIElements.otherFeatures    import   OtherFeatures
from UIElements.softwareSettings import   SoftwareSettings
from UIElements.viewMenu         import   ViewMenu
from UIElements.runMenu          import   RunMenu
from UIElements.scrollLabel      import   ScrollLabel
from UIElements.connectMenu      import   ConnectMenu
from UIElements.diagnosticsMenu  import   Diagnostics
from UIElements.manualControls   import   ManualControl
from DataStructures.data         import   Data
'''

Main UI Program

'''

class GroundControlApp(App):
    
    def build(self):
        interface = FloatLayout()
        self.dataBack = Data()
        
        #create queues
        message_queue = Queue.Queue()
        gcode_queue = Queue.Queue()
        quick_queue = Queue.Queue()
        
        screenControls = GridLayout(rows = 1, size_hint=(1, .05), pos = (0,Window.height - 50))
        
        btn1 = Button(text='Control', size_hint=(.5, .5))
        btn1.bind(on_press=self.showFront)
        screenControls.add_widget(btn1)
        
        btn2 = Button(text='Options', size_hint=(.5, .5))
        btn2.bind(on_press=self.showFeatures)
        screenControls.add_widget(btn2)
        
        
        btn3 = Button(text='Settings', size_hint=(.5, .5))
        btn3.bind(on_press=self.showSettings)
        screenControls.add_widget(btn3)
        
        #interface.add_widget(screenControls)
        
        layout = AnchorLayout(anchor_x='center', anchor_y='top')
        #btn = Button(text='Hello World', size_hint=(.1,.05))
        layout.add_widget(screenControls)
        
        interface.add_widget(layout)
        
        self.sm = ScreenManager(transition=SlideTransition(), size_hint=(1, .95), pos = (0,0), clearcolor=(1,1,1,1))
        
        self.frontpage = FrontPage(name='FrontPage')
        self.sm.add_widget(self.frontpage)
        
        self.otherfeatures = OtherFeatures(name='OtherFeatures')
        self.sm.add_widget(self.otherfeatures)
        
        self.softwaresettings = SoftwareSettings(name='SoftwareSettings')
        self.sm.add_widget(self.softwaresettings)
        
        interface.add_widget(self.sm)
        
        self.otherfeatures.connectmenu.setupQueues(message_queue, gcode_queue, quick_queue)
        self.frontpage.setupQueues(message_queue, gcode_queue, quick_queue)
        
        self.otherfeatures.viewmenu.setGcodeLocation(self.frontpage.gcodecanvas)
        
        Clock.schedule_interval(self.otherfeatures.connectmenu.updatePorts, .5)
        Clock.schedule_interval(self.runPeriodically, .01)
        
        Clock.schedule_once(self.otherfeatures.connectmenu.connect, .1)
        
        return interface
    
    '''
    
    Update Functions
    
    '''
    
    def runPeriodically(self, *args):
        if not self.otherfeatures.connectmenu.message_queue.empty(): #if there is new data to be read
            message = self.otherfeatures.connectmenu.message_queue.get()
            if message[0:2] == "pz":
                self.setPosOnScreen(message)
            elif message[0:6] == "gready":
                self.frontpage.gcodecanvas.readyFlag = 1
                if self.frontpage.gcodecanvas.uploadFlag == 1:
                    self.frontpage.sendLine()
                    self.frontpage.gcodecanvas.readyFlag = 0
            
            else:
                try:
                    newText = self.frontpage.consoleText[-30:] + message
                    self.frontpage.consoleText = newText
                except:
                    print "text not displayed correctly"
    
    def setPosOnScreen(self, message):
        
 #       try:
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
        
    
    '''

    Show page functions

    '''
    
    def showFront(self, extra):
        self.sm.current = 'FrontPage'
    
    def showFeatures(self, extra):
        self.sm.current = 'OtherFeatures'
    
    def showSettings(self, extra):
        self.sm.current = 'SoftwareSettings'
    
if __name__ == '__main__':
    GroundControlApp().run()
