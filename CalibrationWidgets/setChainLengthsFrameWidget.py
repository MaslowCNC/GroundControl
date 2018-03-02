'''

This is the widget which creates a frame around the calibration process providing infrastructure like the forwards and back buttons

Each widget which it loads should be largely self contained and either gather a piece of information from the user or set the machine into a known
state regardless of the machine's state when the widget begins.

'''
from   kivy.uix.gridlayout                                  import  GridLayout
from   kivy.properties                                      import  ObjectProperty
from CalibrationWidgets.intro                               import  Intro
from CalibrationWidgets.chooseKinematicsType                import  ChooseKinematicsType
from CalibrationWidgets.chooseChainOverSprocketDirection    import  ChooseChainOverSprocketDirection
from CalibrationWidgets.computeCalibrationSteps             import  ComputeCalibrationSteps
from CalibrationWidgets.setSprocketsVertical                import  SetSprocketsVertical
from CalibrationWidgets.measureDistBetweenMotors            import  MeasureDistBetweenMotors
from CalibrationWidgets.vertDistToMotorsGuess               import  VertDistToMotorsGuess
from CalibrationWidgets.measureOutChains                    import  MeasureOutChains
from CalibrationWidgets.adjustZCalibrationDepth             import  AdjustZCalibrationDepth
from CalibrationWidgets.rotationRadiusGuess                 import  RotationRadiusGuess
from CalibrationWidgets.triangularCalibration               import  TriangularCalibration
from CalibrationWidgets.distBetweenChainBrackets            import  DistBetweenChainBrackets
from CalibrationWidgets.reviewMeasurements                  import  ReviewMeasurements
from CalibrationWidgets.quadTestCut                         import  QuadTestCut
from CalibrationWidgets.finish                              import  Finish
from   kivy.app                                             import  App


class SetChainLengthsFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    listOfCalibrationSteps = []
    currentStepNumber = 0
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        
        App.get_running_app().data.calibrationInProcess = True
        
        #load steps
        setSprocketsVertical =  SetSprocketsVertical()
        self.listOfCalibrationSteps.append(setSprocketsVertical)
        
        measureOutChains =  MeasureOutChains()
        self.listOfCalibrationSteps.append(measureOutChains)
        
        
        
        self.loadStep(0)
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        App.get_running_app().data.calibrationInProcess = False
        App.get_running_app().data.message_queue.put("Message: Notice: Exiting the process early may result in incorrect calibration.")
        
        #remove the old widget
        try:
            self.cFrameWidgetSpace.remove_widget(self.currentWidget)
        except:
            pass #there was no widget to remove
        
        self.done()
    
    def loadNextStep(self):
        '''
        
        Called to trigger a loading of the next slide
        
        '''
        
        self.currentStepNumber = self.currentStepNumber + 1
        self.loadStep(self.currentStepNumber)
    
    def back(self):
        '''
        
        Re-load the previous step
        
        '''
        self.currentStepNumber = self.currentStepNumber - 1
        self.loadStep(self.currentStepNumber)
        
    def loadStep(self, stepNumber):
        
        #remove the old widget
        try:
            self.cFrameWidgetSpace.remove_widget(self.currentWidget)
        except:
            pass #there was no widget to remove
        
        try:
            #load the new widget
            self.currentWidget = self.listOfCalibrationSteps[self.currentStepNumber]
            
            #initialize the new widget
            self.currentWidget.readyToMoveOn = self.loadNextStep
            self.currentWidget.on_Enter()
            self.cFrameWidgetSpace.add_widget(self.currentWidget)
        except IndexError:
            #the calibration has run out of steps
            pass