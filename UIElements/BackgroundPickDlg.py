from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   kivy.graphics.texture                     import Texture
from   kivy.graphics							 import Rectangle
from   kivy.clock                                import Clock
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs


import cv2
import numpy as np
import dumper

class BackgroundPickDlg(GridLayout, MakesmithInitFuncs):
    instructionText = StringProperty("Pickem")
    
    def __init__(self, data, **kwargs):
        super(BackgroundPickDlg, self).__init__(**kwargs)
        self.data = data
        self.centers=[]
         
        #Load the texture
        self.instructionText = "Pick the Top-Left Alignment Dot"
        self.img = self.data.backgroundImage #ToDo: This should be local
        w = self.img.shape[0]
        h = self.img.shape[1]
        
        self.texture = Texture.create(size=(h,w))   #Create Texture (only needs to be done once; blit to it as much as you like.
        
        #ToDo: I don't know why I can't simply say self.Drawing here, but it explodes
        #So instead, I look for an object with the text 'Foo'
        self.Drawing = None
        for widget in self.walk():
            try:
                if widget.text == 'Foo':
                    self.Drawing=widget
            except (AttributeError):
                pass

        #Can't draw yet... we're not on screen!
        Clock.schedule_once(self.redraw)
        
    def redraw(self, *args):
        print "Redraw:", self.centers
        self.instructionText = [
            "Pick the Top-Left Alignment Dot...", 
            "Pick the Top-Right Alignment Dot...", 
            "Pick the Bottom-Left Alignment Dot...", 
            "Pick the Bottom-Right Alignment Dot."][len(self.centers)]

        buf = self.img.tobytes() # then, convert the array to a ubyte string
        self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte') # and blit the buffer -- note that OpenCV format is BGR
        self.texture.flip_vertical() #OpenGL is upside down...

        #print self.Drawing
        with self.Drawing.canvas:
            Rectangle(texture=self.texture, pos=self.Drawing.pos, size=self.Drawing.size)
            pass
    
    def clear(self):
        #clear the list
        self.centers=[]
        
        #present the original image
        self.img=self.data.backgroundImage
        self.redraw()
    
    def untouched(self, touch):
        print "UNT"
        center = (int(touch.x), int(touch.y))
        print center
        self.centers.append(center)
        self.texture.flip_vertical()
        cv2.circle(self.img, center, 20, (255, 0, 0), -1)
        if len(self.centers) < 4 or True:
            self.redraw()
        else:
            pass    #How do you do a callback()?

    #ToDo: OnTouch/OnMove, pop-up a magnified thing so you can see crosshairs
    def touched(self, touch):
        print "TCH"
        
    def touchmove(self, touch):
        print "TMO"
