from   kivy.uix.gridlayout                       import   GridLayout
from   UIElements.loadDialog                     import   LoadDialog
from   UIElements.scrollableTextPopup            import   ScrollableTextPopup
from   kivy.uix.popup                            import   Popup
import re
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from os                                          import    path





class ViewMenu(GridLayout, MakesmithInitFuncs):
    
    def openFile(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        content.path = path.dirname(self.data.gcodeFile)
        if content.path is "": 
            content.path = path.expanduser('~')
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def reloadGcode(self):
        '''
        
        Trigger a reloading of the gcode file
        
        '''
        
        filePath = self.data.gcodeFile
        self.data.gcodeFile = ""
        self.data.gcodeFile = filePath
        
        #close the parent popup
        self.parentWidget.close()
    
    def load(self, path, filename):
        '''
        
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        #locate the file
        filename = filename[0]
        
        self.data.gcodeFile = filename
        self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))
        self.data.config.write()
        
        self.dismiss_popup()
        
        #close the parent popup
        self.parentWidget.close()
        

    def show_gcode(self):
        '''
        
        Display the currently loaded gcode in a popup
        
        It would be cool if you could run the program stepping through using this popup
        
        '''
        
        popupText = ""
        if len(self.data.gcode) is 0:
            popupText =  "No gcode to display"
        else:
            for lineNum, gcodeLine in enumerate(self.data.gcode):
                if lineNum<447:
                    popupText = popupText + gcodeLine + "\n"
                else:
                    popupText = popupText + "...\n...\n...\n"
                    break
                
        content = ScrollableTextPopup(cancel = self.dismiss_popup, text = popupText)
        self._popup = Popup(title="Gcode", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()
