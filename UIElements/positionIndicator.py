from DataStructures.makesmithInitFuncs     import MakesmithInitFuncs
from kivy.uix.widget                       import Widget


class PositionIndicator(Widget):
    '''
    
    An instance of this widget creates cross-hairs which indicate the machine
    position on the screen.
    
    '''
    def move(self, xloc, yloc):
        self.pos = (xloc, yloc)