'''

The widget which lets you choose which direction your chain passes over the sprocket

'''
from   kivy.uix.gridlayout                          import   GridLayout
from   kivy.properties                              import   ObjectProperty
from   kivy.app                                     import   App

class ChooseChainOverSprocketDirection(GridLayout):
    readyToMoveOn   = ObjectProperty(None)
    
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        print "choose sprocket direction on enter ran"
    
    def setChainToTop(self):
        '''
        
        Write into the settings that the chain direction is to the left
        
        '''
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', 'Top')
        App.get_running_app().data.config.write()
        self.on_Exit()
    
    def setChainToBottom(self):
        '''
        
        Write into the settings that the chain direction is to the right
        
        '''
        App.get_running_app().data.config.set('Advanced Settings', 'chainOverSprocket', 'Bottom')
        App.get_running_app().data.config.write()
        self.on_Exit()
    
    def on_Exit(self):
        '''
        
        This function runs when the step is completed
        
        '''
        print "choose kinematics type on exit ran"
        self.readyToMoveOn()