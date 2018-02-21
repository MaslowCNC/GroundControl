'''

This widget computes which calibration steps will be needed for a given machine setup

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class ComputeCalibrationSteps(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    setListOfSteps  = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "compute calibration steps on enter"
        
        
        '''
        chainDir = App.get_running_app().data.config.get('Advanced Settings', 'chainOverSprocket')
        
        listOfSteps = []
        
        if chainDir == 'Top':
            print "top recognized"
            chooseKinematicsType = ChooseKinematicsType()
            listOfSteps.append(chooseKinematicsType)
            #set to 12'
            
            #measure dist between motors 
        else:
            print "bottom recognized"
        '''
        self.setListOfSteps()
        self.on_Exit()
    
    def on_Exit(self):
        '''
        
        This function run when the process is completed or quit is pressed
        
        '''
        print "compute calibration steps on exit"
        self.readyToMoveOn()
