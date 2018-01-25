from kivy.uix.floatlayout                      import   FloatLayout
from kivy.uix.popup                            import   Popup
from UIElements.otherFeatures                  import   OtherFeatures
from UIElements.Background					   import	Background
from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from UIElements.buttonTemplate                 import   ButtonTemplate
from UIElements.backgroundMenu                 import   BackgroundMenu
import numpy as np

def adjust_background(self, increment):
    '''
    Adjust the background and refresh the UIElements
    '''
    img = self.data.backgroundImage
    if img is not None:
        img = img.astype('int16')       #Expand the range
        img += increment                #Do the math
        np.clip(img, 0, 255, out=img)   #Clip the image (no wrapping!)
        img = img.astype('uint8')       #Convert it back
        self.data.backgroundImage = img #Reset it
        
        #Trigger a reload
        filePath = self.data.gcodeFile
        self.data.gcodeFile = ""
        self.data.gcodeFile = filePath

class ScreenControls(FloatLayout, MakesmithInitFuncs):
    
    
    def setButtonAppearance(self):
        '''
        
        Called on creation to set up links to button background textures
        
        '''
        #For some reason, my +/- buttons didn't work with the old way, so I'll set everything.
        for widget in self.walk():
            if "ButtonTemplate"in str(type(widget)):
                widget.btnBackground            = self.data.iconPath + 'Generic.png'
                widget.textColor                = self.data.fontColor
         
    def show_actions(self):
        '''
        
        Open A Pop-up To Allow User Actions
        
        Creates a new pop-up allows the user to do things like open a file.
        
        '''
        content = OtherFeatures()
        content.setUpData(self.data)
        content.close = self.close_popup
        self._popup = Popup(title="Actions", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def close_popup(self):
        '''
        Close pop-up
        '''
        self._popup.dismiss()
		
    def open_background(self):
        '''
        Open A Pop-up To Manage the Canvas Background
        '''
        content = Background()
        content.setUpData(self.data)
        content.close = self.close_popup
        self._popup = Popup(title="Background Picture", content=content, size_hint = (0.5,0.5))
        self._popup.open()
