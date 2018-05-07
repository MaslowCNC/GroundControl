from   kivy.uix.gridlayout                import   GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
from   kivy.app                           import   App
import global_variables

class ComputeChainCorrectionFactors(GridLayout):
    '''
    
    Compute the chain correction factors based on values entered prevously.
    
    '''
    data                        =  ObjectProperty(None) #linked externally
    readyToMoveOn               = ObjectProperty(None)
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
        
        try:
        
            self.leftCorrectionFactor = (abs(self.data.motorsDist - self.data.leftChainMeasurement)/self.data.leftChainMeasurement)*100.0
            self.rightCorrectionFactor = (abs(self.data.motorsDist - self.data.rightChainMeasurement)/self.data.rightChainMeasurement)*100.0
            
            self.selfText.text = ("When measured manually: " + str(self.data.motorsDist) 
                + "\nWhen measured with the left chain:" + str(self.data.leftChainMeasurement) 
                + "\nWhen measured with the right chain:" + str(self.data.rightChainMeasurement)
                + "\n\nLeft chain correction factor: " + str(self.leftCorrectionFactor)
                + "\nRight chain correction factor: " + str(self.rightCorrectionFactor)
                )
        except:
            self.selfText.text = "unable to compute correction factors"
    
    def loadNextStep(self):
        
        self.data.config.set('Advanced Settings', 'leftChainTolerance', self.leftCorrectionFactor)
        self.data.config.set('Advanced Settings', 'rightChainTolerance', self.rightCorrectionFactor)
        
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        pass
