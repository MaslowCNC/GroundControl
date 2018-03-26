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
from CalibrationWidgets.removeChains                        import  RemoveChains
from CalibrationWidgets.adjustZCalibrationDepth             import  AdjustZCalibrationDepth
from CalibrationWidgets.rotationRadiusGuess                 import  RotationRadiusGuess
from CalibrationWidgets.triangularCalibration               import  TriangularCalibration
from CalibrationWidgets.distBetweenChainBrackets            import  DistBetweenChainBrackets
from CalibrationWidgets.reviewMeasurements                  import  ReviewMeasurements
from CalibrationWidgets.quadTestCut                         import  QuadTestCut
from CalibrationWidgets.finish                              import  Finish
from   kivy.app                                             import  App


class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    listOfCalibrationSteps = []
    currentStepNumber = 0
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        
        App.get_running_app().data.calibrationInProcess = True
        
        #generate the first two steps because they are always the same
        intro =  Intro()
        self.listOfCalibrationSteps.append(intro)
        
        chooseKinematicsType                        = ChooseKinematicsType()
        self.listOfCalibrationSteps.append(chooseKinematicsType)
        
        vertDistGuess                               = VertDistToMotorsGuess()
        self.listOfCalibrationSteps.append(vertDistGuess)
        
        setTo12                                     = SetSprocketsVertical()
        self.listOfCalibrationSteps.append(setTo12)
        
        measureMotorDist                            = MeasureDistBetweenMotors()
        self.listOfCalibrationSteps.append(measureMotorDist)
        
        chooseChainOverSprocketDirection             = ChooseChainOverSprocketDirection()
        self.listOfCalibrationSteps.append(chooseChainOverSprocketDirection)
        
        reviewMeasurements                          = ReviewMeasurements()
        self.listOfCalibrationSteps.append(reviewMeasurements)
        
        computeCalibrationSteps                     = ComputeCalibrationSteps()
        computeCalibrationSteps.setupListOfSteps    = self.addSteps
        self.listOfCalibrationSteps.append(computeCalibrationSteps)
        
        self.loadStep(0)
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        App.get_running_app().data.calibrationInProcess = False
        App.get_running_app().data.message_queue.put("Message: Notice: Exiting the calibration process early may result in incorrect calibration.")
        
        #remove the old widget
        try:
            self.cFrameWidgetSpace.remove_widget(self.currentWidget)
        except:
            pass #there was no widget to remove
        
        self.done()
    
    def addSteps(self):
        '''
        
        This function will be called when the ComputeCalibrationSteps step is reached. It will compute which steps are needed for a 
        given frame configuration and add them to the list
        
        '''
        
        if App.get_running_app().data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            #if we're using the top system no extra steps are needed
            pass
        else:
            #if we're using the bottom method we need to remove the chain now and put it back at 12 o'clock
            
            removeChains                                 = RemoveChains()
            self.listOfCalibrationSteps.append(removeChains)
            
            setTo12                                     = SetSprocketsVertical()
            self.listOfCalibrationSteps.append(setTo12)
            
        
        if App.get_running_app().data.config.get('Advanced Settings', 'kinematicsType') == 'Triangular':
            #add rotation radius guess
            rotationRadiusGuess                         = RotationRadiusGuess()
            self.listOfCalibrationSteps.append(rotationRadiusGuess)
            
            #add extend chains
            measureOutChains                                = MeasureOutChains()
            self.listOfCalibrationSteps.append(measureOutChains)
            
            #add set z
            adjustZCalibrationDepth                         = AdjustZCalibrationDepth()
            self.listOfCalibrationSteps.append(adjustZCalibrationDepth)
            
            #add triangular kinematics
            triangularCalibration                       = TriangularCalibration()
            self.listOfCalibrationSteps.append(triangularCalibration)
        else:
            
            #add extend chains
            measureOutChains                                = MeasureOutChains()
            self.listOfCalibrationSteps.append(measureOutChains)
            
            #add set z
            adjustZCalibrationDepth                         = AdjustZCalibrationDepth()
            self.listOfCalibrationSteps.append(adjustZCalibrationDepth)
            
            #Ask for guess of attachment spacing
            distBetweenChainBrackets                    = DistBetweenChainBrackets()
            self.listOfCalibrationSteps.append(distBetweenChainBrackets)
            #Do quadrilateral test cut
            quadTestCut                                 = QuadTestCut()
            self.listOfCalibrationSteps.append(quadTestCut)
            
            #App.get_running_app().data.message_queue.put("Message: You have chosen a configuration which is not currently supported by the calibration process. Check back soon")
            #self.done()
        
        #one last review
        reviewMeasurements                          = ReviewMeasurements()
        self.listOfCalibrationSteps.append(reviewMeasurements)
        
        #add finish step
        finish              = Finish()
        finish.done         = self.done
        self.listOfCalibrationSteps.append(finish)
    
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
            self.currentWidget.on_Exit()
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