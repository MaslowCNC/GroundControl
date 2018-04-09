from   kivy.uix.gridlayout                import   GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
from   kivy.app                           import   App
import global_variables

class ManualCalibration(GridLayout):
    '''
    
    Provides a quick way to get a machine going. This is not intended to be a replacement for the calibration process, just a quick way to get
    someone past the frustration of not being able to calibrate.
    
    '''
    data                        =  ObjectProperty(None) #linked externally
    readyToMoveOn               = ObjectProperty(None)
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
    
    def switchUnits(self):
        if self.unitsBtnT.text == 'Units: mm':
            self.unitsBtnT.text = 'Units: inches'
        else:
            self.unitsBtnT.text = 'Units: mm'
    
    def enterValues(self):
        '''
        
        Manually enter the machine dimensions
        
        '''
        try:
            motorsDist      = float(self.motorsDist.text)
            rotationRadius  = float(self.rotationRadius.text)
            motorsVertical  = float(self.vertMeasure.text)
            
            #convert from inches to mm if needed
            if self.unitsBtnT.text == 'Units: inches':
                motorsDist      = motorsDist*25.4
                rotationRadius  = rotationRadius*25.4
                motorsVertical  = motorsVertical*25.4
            
            if self.chooseKinematics.text != 'Triangular':
                self.data.message_queue.put("Message: Quadrilateral kinematics not yet supported by manual calibration")
                return
            
            # Update machine parameters

            self.data.config.set('Maslow Settings', 'motorOffsetY', str(motorsVertical))
            self.data.config.set('Maslow Settings', 'motorSpacingX', str(motorsDist))
            self.data.config.set('Advanced Settings', 'rotationRadius', str(rotationRadius))
            self.data.config.set('Advanced Settings', 'kinematicsType', 'Triangular')
            self.data.config.set('Advanced Settings', 'chainOverSprocket', self.chooseFeedDir.text)
            
            self.loadNextStep()
            
        except Exception as e:
            print e
    
    def loadNextStep(self):
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        pass
