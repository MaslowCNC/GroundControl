from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from   kivy.graphics.texture                     import Texture
from   kivy.graphics							 import Rectangle
from   kivy.clock                                import Clock
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs


import cv2
import numpy as np

class BackgroundPickDlg(GridLayout, MakesmithInitFuncs):
    instructionText = StringProperty("Pickem")
    armed = False
    
    def __init__(self, data, **kwargs):
        super(BackgroundPickDlg, self).__init__(**kwargs)
        self.data = data
        self.centers=[]
         
        #Load the texture
        self.instructionText = "Pick the Top-Left Alignment Dot"
        self.img = self.data.backgroundImage.copy()
        self.h = self.img.shape[0]
        self.w = self.img.shape[1]
        
        self.texture = Texture.create(size=(self.w,self.h))   #Create Texture (only needs to be done once; blit to it as much as you like.
        
        #ToDo: I don't know why I can't simply say self.Drawing here, but it explodes
        #So instead, I look for an object with the text 'Foo'
        self.Drawing = None
        for widget in self.walk():
            try:
                if widget.text == 'Foo':
                    self.Drawing=widget
            except (AttributeError):
                pass

        self.Drawing.bind(on_touch_down=self.touched)
        self.Drawing.bind(on_touch_move=self.touchmove)
        self.Drawing.bind(on_touch_up=self.untouched)
        
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
        self.texture.flip_vertical()
        self.img=self.data.backgroundImage.copy()
        self.redraw()

    def closeit(self):
        self.close(self)
    
    def untouched(self, isntance, touch):
        if not self.armed:
            return 1
            
        self.armed=False
            
        #ToDo... Maybe I should use a scatter to do these transformations?
        #Get canvas zero and size, since touch comes back to us in absolute screen coordinates
        x0 = self.Drawing.pos[0]
        y0 = self.Drawing.pos[1]
        sx = self.Drawing.size[0]
        sy = self.Drawing.size[1]
        
        if touch.x < x0 or touch.x > x0+sx or touch.y > y0+sy or touch.y < y0:
            return 1    #Outside our bounding box!

        #Yes, this is goofy, but it works:  Y is backwards
        x = (touch.x-x0)/sx * self.w
        y = (sy-(touch.y-y0))/sy * self.h

        center = (int(x), int(y))
        self.centers.append(center)
        self.texture.flip_vertical()
        cv2.circle(self.img, center, 25, (255, 255, 0), -1) #Cyan
        if len(self.centers) < 4:
            self.redraw()
        else:
            self.texture.flip_vertical()    #I was supposed to be working with a copy... why should I need to do this?!
            self.close(self)                #All points picked, return to caller
        
    #ToDo: OnTouch/OnMove, pop-up a magnified thing so you can see crosshairs
    def touched(self, isntance,  touch):
        self.armed=True
        
    def touchmove(self, isntance, touch):
        pass
