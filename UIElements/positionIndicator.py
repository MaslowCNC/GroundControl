from DataStructures.makesmithInitFuncs     import MakesmithInitFuncs
from kivy.uix.widget                       import Widget
from kivy.graphics                         import Color
from kivy.properties                       import ObjectProperty
from kivy.properties                       import NumericProperty


class PositionIndicator(Widget):
    '''
    
    An instance of this widget creates cross-hairs which indicate the machine
    position on the screen.
    
    '''
    INCH            = 25.4
    MILLIMETER       = 1 
    color             = ObjectProperty((1, 1, 1))
    positionErrorRadius = NumericProperty(0)
    
    def setPos(self, xPos, yPos, units):
        '''
        
        Move cross-hairs on UI
        
        '''
        
        if units == "MM":
            crossPosX = xPos*self.MILLIMETER
            crossPosY = yPos*self.MILLIMETER
        elif units == "INCHES":
            crossPosX = xPos*self.INCH
            crossPosY = yPos*self.INCH
        
        self.pos = (crossPosX,crossPosY)
        
    
    def setError(self, positionError, units):
        '''
        
        Set the error circle indicator.
        
        '''
        if units == "MM":
            positionError = positionError*self.MILLIMETER
        elif units == "INCHES":
            positionError = positionError*self.INCH
            
        self.positionErrorRadius = positionError