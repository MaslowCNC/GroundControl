from DataStructures.makesmithInitFuncs     import MakesmithInitFuncs
from kivy.uix.widget                       import Widget


class PositionIndicator(Widget):
    '''
    
    An instance of this widget creates cross-hairs which indicate the machine
    position on the screen.
    
    '''
    INCHES            = 25.4
    MILLIMETERS       = 1 
    
    def setPos(self, xPos, yPos, units):
        '''
        
        Move cross-hairs on UI
        
        '''
        
        if units == "mm":
            self.crossPosX = xPos*self.MILLIMETERS
            self.crossPosY = yPos*self.MILLIMETERS
        elif units == "in":
            self.crossPosX = xPos*self.INCHES
            self.crossPosY = yPos*self.INCHES
        
        
        self.pos = (self.crossPosX,self.crossPosY)