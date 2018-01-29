from   kivy.uix.gridlayout                       import   GridLayout
import re
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs

import cv2
import numpy as np

class BackgroundPickDlg(GridLayout, MakesmithInitFuncs):
    
    def open(self):
        #Load the texture
        self.center=[]
        self.instructions = "Pick the Top-Left Alginment Dot"
        self.img = self.data.backgroundImage #ToDo: This should be local
        self.texture = Texture.create(size=(h,w))
        self.redraw()
        
    def redraw(self):
        print "Redraw"
        self.instructions = [
            "Pick the Top-Left Alignment Dot...", 
            "Pick the Top-Right Alignment Dot...", 
            "Pick the Bottom-Left Alignment Dot...", 
            "Pick the Bottom-Right Alignment Dot."][len(self.centers)]

        buf = self.img.tobytes() # then, convert the array to a ubyte string
        self.texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte') # and blit the buffer -- note that OpenCV format is BGR
        self.texture.flip_vertical() #OpenGL is upside down...
        Rectangle(texture=self.texture, pos=(0,0), size=(800,600))
    
    def clear(self):
        #clear the list
        self.centers=[]
        self.instructions = "Pick the Top-Left Alginment Dot"
        
        #present the original image
        self.img=data.backgroundImage
        self.redraw()
    
    def untouched(self, touch):
        print "untouch"
        self.centers.add(touch.x, touch.y)
        cv2.circle(img, center, 10, (255, 0, 0), -1)
        if len(self.centers) < 4:
            self.redraw()
        else:
            pass    #How do you do a callback()?

    #ToDo: OnTouch/OnMove, pop-up a magnified thing
    def touched(self, touch):
        print "touch"
        pass
        
    def touchmove(self, touch):
        print "tmove"
        pass
        
        