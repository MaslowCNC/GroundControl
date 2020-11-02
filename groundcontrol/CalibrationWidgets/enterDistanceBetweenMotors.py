from   kivy.uix.gridlayout                import   GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
from   kivy.app                           import   App
import global_variables

class EnterDistanceBetweenMotors(GridLayout):
    '''
    
    Enter the manually measured distance between the motors.
    
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
            
            #convert from inches to mm if needed
            if self.unitsBtnT.text == 'Units: inches':
                motorsDist      = motorsDist*25.4
            
            #subtract off the width of the motors
            
            motorsDist = motorsDist - 40.4
            
            self.data.motorsDist = motorsDist
            
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
