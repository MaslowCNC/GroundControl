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

Other Imports

'''

import Queue

'''

Internal Module Imports

'''

from UIElements.frontPage        import   FrontPage
from UIElements.screenControls   import   ScreenControls
from UIElements.gcodeCanvas      import   GcodeCanvas
from UIElements.otherFeatures    import   OtherFeatures
from UIElements.softwareSettings import   SoftwareSettings
from UIElements.viewMenu         import   ViewMenu
from UIElements.runMenu          import   RunMenu
from UIElements.connectMenu      import   ConnectMenu
from UIElements.diagnosticsMenu  import   Diagnostics
from UIElements.manualControls   import   ManualControl
from DataStructures.data         import   Data
'''

Main UI Program

'''

class GroundControlApp(App):
    
    def build(self):
        interface       =  FloatLayout()
        self.dataBack   =  Data()
        
        #create queues
        message_queue   =  Queue.Queue()
        gcode_queue     =  Queue.Queue()
        quick_queue     =  Queue.Queue()
        
        
        self.frontpage = FrontPage(name='FrontPage')
        interface.add_widget(self.frontpage)
        
        self.screenControls = ScreenControls()
        interface.add_widget(self.screenControls)
        
        '''
        Initializations
        '''
        
        self.frontpage.setupQueues(message_queue, gcode_queue, quick_queue)
        
        self.frontpage.gcodecanvas.initialzie()
        
        
        '''
        Scheduling
        '''
        
        Clock.schedule_interval(self.runPeriodically, .01)
        
        return interface
    
    '''
    
    Update Functions
    
    '''
    
    def runPeriodically(self, *args):
        pass
        '''
        this block should be handled within the appropriate widget
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
        '''
    
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
        
    
if __name__ == '__main__':
    GroundControlApp().run()
