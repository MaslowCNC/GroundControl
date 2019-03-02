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
from CalibrationWidgets.finishSetChainLengths               import  FinishSetChainLengths
from CalibrationWidgets.manualCalibration                   import  ManualCalibration
from CalibrationWidgets.enterDistanceBetweenMotors          import  EnterDistanceBetweenMotors
from CalibrationWidgets.measureOneChain                     import  MeasureOneChain
from CalibrationWidgets.computeChainCorrectionFactors       import  ComputeChainCorrectionFactors
from CalibrationWidgets.wipeOldCorrectionValues             import  WipeOldCorrectionValues
from CalibrationWidgets.chooseHoleyOrTriangularCalibration  import  ChooseHoleyOrTriangularCalibration
from CalibrationWidgets.holeyCalMeasurements                import  HoleyCalMeasurements
from CalibrationWidgets.holeyCalOptimize                    import  HoleyCalOptimize
from CalibrationWidgets.holeyCalCut                         import  HoleyCalCut
from kivy.app                                               import  App
from kivy.lang                                              import  Builder
from kivy.uix.label                                         import  Label
from kivy.properties                                        import  ListProperty

Builder.load_string("""
<ColoredLabel>:
  bcolor: 1, 1, 1, 1
  canvas.before:
    Color:
      rgba: self.bcolor
    Rectangle:
      pos: self.pos
      size: self.size
""")
    
class ColoredLabel(Label):
  bcolor = ListProperty([0,0,0,.5])

class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    listOfCalibrationSteps = []
    currentStepNumber = 0
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        
        App.get_running_app().data.calibrationInProcess = True
        
        
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
    
    def setupFullCalibration(self):
        
        #ensure that there are no widgets in the deck when we start
        self.listOfCalibrationSteps = []
        
        #load the first steps in the calibration process because they are always the same
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
    
    def setupJustChainsCalibration(self):
        '''
        
        Calling this function sets up the calibration process to show just the steps to calibrate the chain lengths
        
        '''
        
        #ensure that there are no widgets in the deck when we start
        self.listOfCalibrationSteps = []
        
        #load steps
        setSprocketsVertical =  SetSprocketsVertical()
        self.listOfCalibrationSteps.append(setSprocketsVertical)
        
        measureOutChains =  MeasureOutChains()
        self.listOfCalibrationSteps.append(measureOutChains)
        
        finishSetChainLengths =  FinishSetChainLengths()
        finishSetChainLengths.done         = self.done
        self.listOfCalibrationSteps.append(finishSetChainLengths)
    
    def setupJustTriangularTestCuts(self):
        '''
        
        Calling this function sets up the calibration process to show just the steps cut the triangular test pattern
        
        '''
        
        #ensure that there are no widgets in the deck when we start
        self.listOfCalibrationSteps = []
        
        #add triangular kinematics
        triangularCalibration                       = TriangularCalibration()
        self.listOfCalibrationSteps.append(triangularCalibration)
        
        #one last review
        reviewMeasurements                          = ReviewMeasurements()
        self.listOfCalibrationSteps.append(reviewMeasurements)
        
        #add finish step
        finish              = Finish()
        finish.done         = self.done
        self.listOfCalibrationSteps.append(finish)
    
    def setupManualCalibration(self):
        '''
        
        Calling this function sets up the calibration process to show an option to enter manual machine dimensions
        
        '''
        
        #ensure that there are no widgets in the deck when we start
        self.listOfCalibrationSteps = []
        
        #add manual calibation card
        manualCalibration                       = ManualCalibration()
        self.listOfCalibrationSteps.append(manualCalibration)
        
        #one last review
        reviewMeasurements                          = ReviewMeasurements()
        self.listOfCalibrationSteps.append(reviewMeasurements)
        
        #add finish step
        finish              = Finish()
        finish.done         = self.done
        self.listOfCalibrationSteps.append(finish)
    
    def setupMeasureChainTolerances(self):
        '''
        
        Calling this function sets up the process with the cards to measure the chain tolerances
        
        '''
        
        #ensure that there are no widgets in the deck when we start
        self.listOfCalibrationSteps = []
        
        #enter manual measurement of distance between motors
        enterDistanceBetweenMotors                       = EnterDistanceBetweenMotors()
        self.listOfCalibrationSteps.append(enterDistanceBetweenMotors)
        
        #enter manual measurement of distance between motors
        wipeOldCorrectionValues                       = WipeOldCorrectionValues()
        self.listOfCalibrationSteps.append(wipeOldCorrectionValues)
        
        #set to 12
        setTo12                                          = SetSprocketsVertical()
        self.listOfCalibrationSteps.append(setTo12)
        
        #extend left chain and pull tight to measure
        measureOneChain                                  = MeasureOneChain()
        measureOneChain.setDirection('L')
        self.listOfCalibrationSteps.append(measureOneChain)
        
        #set to 12
        setTo12                                          = SetSprocketsVertical()
        self.listOfCalibrationSteps.append(setTo12)
        
        #extend right chain and pull tight to measure
        measureOneChain                                  = MeasureOneChain()
        measureOneChain.setDirection('R')
        self.listOfCalibrationSteps.append(measureOneChain)
        
        #compute values
        computeChainCorrectionFactors                    = ComputeChainCorrectionFactors()
        self.listOfCalibrationSteps.append(computeChainCorrectionFactors)
        
        #finish
        finish              = Finish()
        finish.done         = self.done
        self.listOfCalibrationSteps.append(finish)
    
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
            #Put step with choice of Holey Calibration vs. Triangular Calibration
            ChoiceWid=ChooseHoleyOrTriangularCalibration()
            ChoiceWid.chooseHoleyCalibration=self.addHoleyCalibration
            ChoiceWid.chooseTriangularCalibration=self.addTriangularCalibration
            ChoiceWid.listOfCalibrationSteps=self.listOfCalibrationSteps
            ChoiceWid.done=self.done
            self.listOfCalibrationSteps.append(ChoiceWid)
            
#            #add rotation radius guess
#            rotationRadiusGuess                         = RotationRadiusGuess()
#            self.listOfCalibrationSteps.append(rotationRadiusGuess)
#            
#            #add extend chains
#            measureOutChains                                = MeasureOutChains()
#            self.listOfCalibrationSteps.append(measureOutChains)
#            
#            #add set z
#            adjustZCalibrationDepth                         = AdjustZCalibrationDepth()
#            self.listOfCalibrationSteps.append(adjustZCalibrationDepth)
#            
#            #add triangular kinematics
#            triangularCalibration                       = TriangularCalibration()
#            self.listOfCalibrationSteps.append(triangularCalibration)
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
        
        
            #one last review
            reviewMeasurements                          = ReviewMeasurements()
            self.listOfCalibrationSteps.append(reviewMeasurements)
            
            #add finish step
            finish              = Finish()
            finish.done         = self.done
            self.listOfCalibrationSteps.append(finish)
    
    def addHoleyCalibration(self):
        #add extend chains
        
        measureOutChains                                = MeasureOutChains()
        self.listOfCalibrationSteps.append(measureOutChains)
        
        #add set z
        adjustZCalibrationDepth                         = AdjustZCalibrationDepth()
        self.listOfCalibrationSteps.append(adjustZCalibrationDepth)
        
        #add Cut
        CommonDict=dict()
        cw=HoleyCalCut(CommonDict)
        self.listOfCalibrationSteps.append(cw)
        
        #add Holey Calibration Measurements
        hcm=HoleyCalMeasurements(CommonDict)
        self.listOfCalibrationSteps.append(hcm)
        
        #add Holey Calibration.  
        hco=HoleyCalOptimize(CommonDict)
        self.listOfCalibrationSteps.append(hco)
        
        self.loadNextStep()
        
        
    def addTriangularCalibration(self):
        #add rotation radius guess
        rotationRadiusGuess = RotationRadiusGuess()
        self.listOfCalibrationSteps.append(rotationRadiusGuess)
        
        #add extend chains
        measureOutChains = MeasureOutChains()
        self.listOfCalibrationSteps.append(measureOutChains)
        
        #add set z
        adjustZCalibrationDepth = AdjustZCalibrationDepth()
        self.listOfCalibrationSteps.append(adjustZCalibrationDepth)
        
        #add triangular kinematics
        triangularCalibration = TriangularCalibration()
        self.listOfCalibrationSteps.append(triangularCalibration)
        
        self.addAfterCalSteps()
        
        self.readyToMoveOn()
        
    def addAfterCalSteps(self):
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