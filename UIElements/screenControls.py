from kivy.uix.floatlayout                      import   FloatLayout
from kivy.uix.popup                            import   Popup
from UIElements.otherFeatures                  import   OtherFeatures
from UIElements.Background					   import	Background
from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from UIElements.buttonTemplate                 import   ButtonTemplate
from UIElements.backgroundMenu                 import   BackgroundMenu


class ScreenControls(FloatLayout, MakesmithInitFuncs):
    
    
    def setButtonAppearance(self):
        '''
        
        Called on creation to set up links to button background textures
        
        '''
        self.actionsBtn.btnBackground            = self.data.iconPath + 'Generic.png'
        self.actionsBtn.textColor                = self.data.fontColor
        self.settingsBtn.btnBackground           = self.data.iconPath + 'Generic.png'
        self.settingsBtn.textColor               = self.data.fontColor
        self.backgroundBtn.btnBackground           = self.data.iconPath + 'Generic.png'
        self.backgroundBtn.textColor               = self.data.fontColor
    
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
        content = BackgroundMenu()
        content.setUpData(self.data)
        content.close = self.close_popup
        self._popup = Popup(title="Background Picture", content=content, size_hint = (0.5,0.5))
        self._popup.open()
