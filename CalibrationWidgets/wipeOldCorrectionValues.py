from   kivy.uix.gridlayout                import   GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   kivy.app                           import   App
import global_variables

class WipeOldCorrectionValues(GridLayout):
    '''
    
    Remove the existing values for the chain correction factors to start fresh.
    
    '''
    data                        =  ObjectProperty(None) #linked externally
    readyToMoveOn               = ObjectProperty(None)
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
    
    
    def wipeOldSettings(self):
        '''
        
        Set the current values to zero
        
        '''
        
        self.data.config.set('Advanced Settings', 'leftChainTolerance', 0)
        self.data.config.set('Advanced Settings', 'rightChainTolerance', 0)
        
        self.loadNextStep()
    
    def loadNextStep(self):
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        pass
