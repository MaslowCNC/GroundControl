#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 06:27:30 2019

@author: john
"""

from   kivy.uix.gridlayout                import   GridLayout
from   kivy.properties                    import   ObjectProperty
from   kivy.properties                    import   StringProperty
from   UIElements.touchNumberInput        import   TouchNumberInput
from   kivy.uix.popup                     import   Popup
from   kivy.app                           import   App
import global_variables

class EnterSledWeight(GridLayout):
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
    
    def enterValues(self):
        '''
        
        Manually enter the machine dimensions
        
        '''
        try:
            sledWeight=float(self.ids['sledWeight'].text)
            
            self.data.config.set('Maslow Settings','sledWeight',sledWeight)
            
            self.loadNextStep()
            
        except Exception as e:
            print(e)
    
    def loadNextStep(self):
        self.readyToMoveOn()
    
    def on_Exit(self):
        '''
        
        This function run when the step is completed
        
        '''
        pass
