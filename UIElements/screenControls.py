from kivy.uix.floatlayout                      import   FloatLayout
from kivy.uix.popup                            import   Popup
from UIElements.otherFeatures                  import   OtherFeatures
from UIElements.softwareSettings               import   SoftwareSettings
from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs
from kivy.config                               import ConfigParser


class ScreenControls(FloatLayout, MakesmithInitFuncs):
    
    def show_actions(self):
        '''
        
        Open A Pop-up To Allow User Actions
        
        Creates a new pop-up allows the user to do things like open a file.
        
        '''
        content = OtherFeatures()
        content.setUpData(self.data)
        self._popup = Popup(title="Actions", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        
    
    def show_settings(self):
        '''
        
        Open A Settings Popup
        
        Creates a new pop-up which lets the user see and edit the program settings
        
        '''
        
        config = ConfigParser()
        config.read('settings.ini')

        content = SoftwareSettings()
        
        self._popup = Popup(title="Actions", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()