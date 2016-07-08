from   kivy.uix.gridlayout                            import   GridLayout
from   UIElements.loadDialog                          import   LoadDialog
from   UIElements.scrollableTextPopup                 import   ScrollableTextPopup
from   kivy.uix.popup                                 import   Popup
import re
from DataStructures.makesmithInitializationFunctions  import MakesmithInitializationFunctions





class ViewMenu(GridLayout, MakesmithInitializationFunctions):
    gcodeFilePath = ""
    
    def openFile(self):
        '''
        
        Open A File
        
        Why does this function exist if its just a nicer name for show_load() ?
        
        '''
        self.show_load()
    
    def show_load(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def load(self, path, filename):
        '''
        
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        #locate the file extension
        filename = filename[0]
        fileExtension = filename[-4:]
        
        self.gcodeFilePath = filename
        self.reloadGcode()
        self.dismiss_popup()
    
    def reloadGcode(self):
        '''
        
        This reloads the gcode from the hard drive in case it has been updated. 
        
        '''
        #try:
        filename = self.gcodeFilePath
        filterfile = open(filename, 'r')
        rawfilters = filterfile.read()
        filtersparsed = re.split(r'\s(?=G)|\n|\s(?=g)|\s(?=M)', rawfilters) #splits the gcode into elements to be added to the list
        filtersparsed = [x + ' ' for x in filtersparsed] #adds a space to the end of each line
        filtersparsed = [x.lstrip() for x in filtersparsed]
        filtersparsed = [x.replace('X ','X') for x in filtersparsed]
        filtersparsed = [x.replace('Y ','Y') for x in filtersparsed]
        filtersparsed = [x.replace('Z ','Z') for x in filtersparsed]
        filtersparsed = [x.replace('I ','I') for x in filtersparsed]
        filtersparsed = [x.replace('J ','J') for x in filtersparsed]
        filtersparsed = [x.replace('F ','F') for x in filtersparsed]

        self.data.gcode = filtersparsed
        print self.data.gcode
        filterfile.close() #closes the filter save file
        #except:
        #    if filename is not "":
        #        print "Cannot reopen gcode file. It may have been moved or deleted. To locate it or open a different file use File > Open G-code"
        #    self.gcodeFilePath = ""
    
    def show_gcode(self):
        '''
        
        Display the currently loaded gcode in a popup
        
        It would be cool if you could run the program stepping through using this popup
        
        '''
        
        popupText = ""
        if len(self.gcodeCanvas.gcode) is 0:
            popupText =  "No gcode to display"
        else:
            for gcodeLine in self.gcodeCanvas.gcode:
                popupText = popupText + gcodeLine + "\n"
                
        content = ScrollableTextPopup(cancel = self.dismiss_popup, text = popupText)
        self._popup = Popup(title="Gcode", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()
