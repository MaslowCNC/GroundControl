from kivy.uix.gridlayout               import   GridLayout
from kivy.uix.popup                    import   Popup
from UIElements.otherFeatures          import   OtherFeatures

class ScreenControls(GridLayout):
    
    def show_actions(self):
        '''
        
        Open The Pop-up To Allow User Actions
        
        Creates a new pop-up allows the user to do things like open a file.
        
        '''
        content = OtherFeatures()
        self._popup = Popup(title="Actions", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()