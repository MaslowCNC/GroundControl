'''

This step lets you review your measurements before moving on.

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class ReviewMeasurements(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        
        self.data = App.get_running_app().data
        
        tempString = "Lets review the measurements to make sure everything looks good. You can use the back button to repeat any step.\n\nThe current values are:"
        tempString = tempString + "\nDistance between motors: " + self.data.config.get('Maslow Settings', 'motorSpacingX') + "mm"
        tempString = tempString + "\nVertical motor offset: " + self.data.config.get('Maslow Settings', 'motorOffsetY') + "mm"
        tempString = tempString + "\nKinematics type: " + self.data.config.get('Advanced Settings', 'kinematicsType')
        tempString = tempString + "\nChain over direction: " + self.data.config.get('Advanced Settings', 'chainOverSprocket')
        if self.data.config.get('Advanced Settings', 'kinematicsType') == 'Triangular':
            tempString = tempString + "\nRotation radius: " + self.data.config.get('Advanced Settings', 'rotationRadius') + "mm"
            tempString = tempString + "\nChain sag correction value: " + self.data.config.get('Advanced Settings', 'chainSagCorrection')
        else:
            tempString = tempString + "\nSled mount spacing: " + self.data.config.get('Maslow Settings', 'sledWidth') + "mm"
        
        self.measurementsReadout.text = tempString
    
    def loadNextStep(self):
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        pass