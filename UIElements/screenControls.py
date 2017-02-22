from kivy.uix.floatlayout                      import   FloatLayout
from kivy.uix.popup                            import   Popup
from UIElements.otherFeatures                  import   OtherFeatures
from DataStructures.makesmithInitFuncs         import   MakesmithInitFuncs


class ScreenControls(FloatLayout, MakesmithInitFuncs):
    
    def show_actions(self):
        '''
        
        Open A Pop-up To Allow User Actions
        
        Creates a new pop-up allows the user to do things like open a file.
        
        '''
        content = OtherFeatures()
        content.setUpData(self.data)
        content.cancel = self.close_actions
        self._popup = Popup(title="Actions", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def close_actions(self):
        '''
        Close pop-up
        '''
        self._popup.dismiss()