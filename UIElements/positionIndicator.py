from DataStructures.makesmithInitFuncs     import MakesmithInitFuncs
from kivy.uix.widget                       import Widget

class PositionIndicator(Widget):
    
    def move(self, xloc, yloc):
        print "would move"
        print self.pos
        self.pos = (xloc, yloc)