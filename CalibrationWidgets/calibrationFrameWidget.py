'''

This is the widget which creates a frame around the calibration process providing infrastructure like the forwards and back buttons.

'''
from   kivy.uix.gridlayout                          import  GridLayout
from   kivy.properties                              import  ObjectProperty
from CalibrationWidgets.intro                       import  Intro
from kivy.uix.button import Button

class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        self.currentWidget =  Intro()
        self.currentWidget.readyToMoveOn = self.loadNextStep
        
        self.cFrameWidgetSpace.add_widget(self.currentWidget)
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        self.done()
    
    def loadNextStep(self):
        '''
        
        Called to trigger a loading of the next slide
        
        '''
        print "load next step ran"
        self.cFrameWidgetSpace.remove_widget(self.currentWidget)