from DataStructures.makesmithInitFuncs     import MakesmithInitFuncs
from kivy.uix.widget                       import Widget
from kivy.graphics                         import Color
from kivy.properties                       import ObjectProperty


class PositionIndicator(Widget):
    '''
    
    An instance of this widget creates cross-hairs which indicate the machine
    position on the screen.
    
    '''
    INCHES            = 25.4
    MILLIMETERS       = 1 
    color             = ObjectProperty((1, 1, 1))
    
    def setPos(self, xPos, yPos, units):
        '''
        
        Move cross-hairs on UI
        
        '''
        
        if units == "mm":
            crossPosX = xPos*self.MILLIMETERS
            crossPosY = yPos*self.MILLIMETERS
        elif units == "in":
            crossPosX = xPos*self.INCHES
            crossPosY = yPos*self.INCHES
        
        print "cross pos x"
        print crossPosX
        
        self.pos = (crossPosX,crossPosY)