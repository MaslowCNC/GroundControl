from kivy.uix.floatlayout                      import   FloatLayout
from kivy.uix.popup                            import   Popup
from UIElements.otherFeatures                  import   OtherFeatures
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
        img = img.astype('int16')
        img += increment
        print np.amax(img), np.amin(img)
        np.clip(img, 0, 255, out=img)
        print np.amax(img), np.amin(img)
        img = img.astype('uint8')
        self.data.backgroundImage = img
        
        #Trigger a reload
        filePath = self.data.gcodeFile
        self.data.gcodeFile = ""
        self.data.gcodeFile = filePath

class ScreenControls(FloatLayout, MakesmithInitFuncs):
    
    
    def setButtonAppearance(self):
        '''
        
        Called on creation to set up links to button background textures
        
        '''
        self.actionsBtn.btnBackground            = self.data.iconPath + 'Generic.png'
        self.actionsBtn.textColor                = self.data.fontColor
        self.settingsBtn.btnBackground           = self.data.iconPath + 'Generic.png'
        self.settingsBtn.textColor               = self.data.fontColor
        self.backgroundBtn.btnBackground         = self.data.iconPath + 'Generic.png'
        self.backgroundBtn.textColor             = self.data.fontColor
        #self.backgroundLightBtn.btnBackground    = self.data.iconPath + 'Generic.png'
        #self.backgroundLightBtn.textColor        = self.data.fontColor
        #self.backgroundDarkBtn.btnBackground     = self.data.iconPath + 'Generic.png'
        #self.backgroundDarkBtn.textColor         = self.data.fontColor
         
    def show_actions(self):
        '''
        
        Open A Pop-up To Allow User Actions
        
        Creates a new pop-up allows the user to do things like open a file.
        
        '''
        content = OtherFeatures()
        content.setUpData(self.data)
        content.close = self.close_popupd
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
        content = BackgroundMenu()
        content.setUpData(self.data)
        content.close = self.close_popup
        self._popup = Popup(title="Background Picture", content=content, size_hint = (0.5,0.5))
        self._popup.open()
        
    def brighten_background(self):
        '''
        Brighten the background
        '''
        adjust_background(self,40)
        
    def darken_background(self):
        '''
        Darken the background
        '''
        adjust_background(self,-30)