'''

This is the widget which creates a frame around the calibration process providing infrastructure like the forwards and back buttons

Each widget which it loads should be largely self contained and either gather a piece of information from the user or set the machine into a known
state regardless of the machine's state when the widget begins.

'''
from   kivy.uix.gridlayout                          import  GridLayout
from   kivy.properties                              import  ObjectProperty
from CalibrationWidgets.intro                       import  Intro
from CalibrationWidgets.chooseKinematicsType        import  ChooseKinematicsType


class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        self.currentWidget =  Intro()
        self.currentWidget.readyToMoveOn = self.loadNextStep
        self.currentWidget.on_Enter()
        
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
        
        #remove the old widget
        print "load next step ran"
        self.cFrameWidgetSpace.remove_widget(self.currentWidget)
        #load the new widget
        self.currentWidget = ChooseKinematicsType()
        self.currentWidget.readyToMoveOn = self.loadNextStep
        self.currentWidget.on_Enter()
        self.cFrameWidgetSpace.add_widget(self.currentWidget)