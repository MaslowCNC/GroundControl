from   kivy.uix.gridlayout                       import   GridLayout
from   UIElements.fileBrowser                    import   FileBrowser
from   UIElements.pageableTextPopup              import   PageableTextPopup
from   kivy.uix.popup                            import   Popup
import re
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from os                                          import    path





class BackgroundMenu(GridLayout, MakesmithInitFuncs):

    page = 1
    
    def openBackground(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        #starting path is either where the last opened file was or the users home directory
        startingPath = path.dirname(self.data.backgroundFile)
        if startingPath is "": 
            startingPath = path.expanduser('~')
        
        #We want to filter to show only files that ground control can open
        validFileTypes = self.data.config.get('Ground Control Settings', 'validExtensions').replace(" ", "").split(',')
        validFileTypes = ['*{0}'.format(fileType) for fileType in validFileTypes] #add a '*' to each one to match the format the widget expects
        
        
        content = FileBrowser(select_string='Select', 
                    favorites=[(startingPath, 'Last Location')], 
                    path = startingPath, 
                    filters = validFileTypes)
                    
        content.bind(on_success=self.load,
                         on_canceled=self.dismiss_popup,
                         on_submit=self.load)
        
        #load=self.load, cancel=self.dismiss_popup
        
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    def reloadBackground(self):
        foo
    
    def clear_background(self):
        '''
        
        Clear background
        
        '''
        self.parentWidget.close()

 
    
    def load(self, instance):
        '''
        
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        
        filename = instance.selection[0]
        print(filename)
        
        #close the open file popup
        self.dismiss_popup()
        
        #locate the file
        self.data.gcodeFile = filename
        self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))
        self.data.config.write()

        #close the parent popup
        self.parentWidget.close()
    
    def openBackgroundSettings(self):
        '''
        Open the background settings page
        '''
        #close the parent popup
        self.parentWidget.close()
    
    
    def dismiss_popup(self, *args):
        '''
        
        Close The Pop-up
        
        '''
        self.page = 1
        self._popup.dismiss()
