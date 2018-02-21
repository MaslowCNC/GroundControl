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


class CalibrationFrameWidget(GridLayout):
    done   = ObjectProperty(None)
    listOfCalibrationSteps = []
    currentStepNumber = 0
    
    def on_Enter(self):
        '''
        
        Called the first time the widget is created
        
        '''
        
        #generate the first two steps because they are always the same
        intro =  Intro()
        self.listOfCalibrationSteps.append(intro)
        
        chooseChainOverSprocketDirection = ChooseChainOverSprocketDirection()
        self.listOfCalibrationSteps.append(chooseChainOverSprocketDirection)
        
        chooseKinematicsType = ChooseKinematicsType()
        self.listOfCalibrationSteps.append(chooseKinematicsType)
        
        chooseChainOverSprocketDirection = ChooseChainOverSprocketDirection()
        self.listOfCalibrationSteps.append(chooseChainOverSprocketDirection)
        
        computeCalibrationSteps = ComputeCalibrationSteps()
        computeCalibrationSteps.setupListOfSteps = self.addSteps
        self.listOfCalibrationSteps.append(computeCalibrationSteps)
        
        chooseKinematicsType = ChooseKinematicsType()
        self.listOfCalibrationSteps.append(chooseKinematicsType)
        
        self.loadStep(0)
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        self.done()
    
    def addSteps(self):
        '''
        
        This function will be called when the ComputeCalibrationSteps step is reached. It will compute which steps are needed for a 
        given frame configuration and add them to the list
        
        '''
        print "the add steps function ran"
        
        '''
        
        Can we split this into steps first relating to the chain direction over/under and then to kinematics type? I think we can
        
        If chain on top of sprockets then:
            Set to 12'oclock
            Measure dist between motors
        
        If chain on bottom of sprockets  -- For now just print "this is not a supported configuration
            Set to 12'oclock
            Measure dist between motors
            Remove chain
            Reset to 12 o'clock
        
        For either:
            Extend chains
            Attach sled
            Set Z
        
        For triangular kinematics:
            Ask for rotation radius
            Do triangular test cut
        
        For quadrilateral kinematics:
            Ask for guess of attachment spacing
            Do quadrilateral test cut
        
        '''
        
        #Set to 12'oclock
        
    
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
        print "load next step ran"
        try:
            self.cFrameWidgetSpace.remove_widget(self.currentWidget)
        except:
            pass #there was no widget to remove
            
        #load the new widget
        self.currentWidget = self.listOfCalibrationSteps[self.currentStepNumber]
        
        #initialize the new widget
        self.currentWidget.readyToMoveOn = self.loadNextStep
        self.currentWidget.on_Enter()
        self.cFrameWidgetSpace.add_widget(self.currentWidget)