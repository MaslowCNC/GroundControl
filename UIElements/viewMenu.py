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
        content.path = path.dirname(self.data.gcodeFile)
        if content.path is "": 
            content.path = path.expanduser('~')
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
        
        self.data.gcodeFile = filename
        self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))
        self.data.config.write()
        
        self.reloadGcode()
        self.dismiss_popup()
        
        #close the parent popup
        self.parentWidget.close()
    
    def reloadGcode(self):
        '''
        
        This reloads the gcode from the hard drive in case it has been updated. 
        
        '''
        filename = self.data.gcodeFile
        try:
            filterfile = open(filename, 'r')
            rawfilters = filterfile.read()
            filtersparsed = re.sub(r'\(([^)]*)\)','',rawfilters) #removes mach3 style gcode comments
            filtersparsed = re.sub(r';([^\n]*)\n','',filtersparsed) #removes standard ; intiated gcode comments
            filtersparsed = re.split(r'\s(?=G)|\n|\s(?=g)|\s(?=M)', filtersparsed) #splits the gcode into elements to be added to the list
            filtersparsed = [x + ' ' for x in filtersparsed] #adds a space to the end of each line
            filtersparsed = [x.lstrip() for x in filtersparsed]
            filtersparsed = [x.replace('X ','X') for x in filtersparsed]
            filtersparsed = [x.replace('Y ','Y') for x in filtersparsed]
            filtersparsed = [x.replace('Z ','Z') for x in filtersparsed]
            filtersparsed = [x.replace('I ','I') for x in filtersparsed]
            filtersparsed = [x.replace('J ','J') for x in filtersparsed]
            filtersparsed = [x.replace('F ','F') for x in filtersparsed]

            self.data.gcode = filtersparsed
            
            filterfile.close() #closes the filter save file
        except:
            if filename is not "":
                print "Cannot reopen gcode file. It may have been moved or deleted. To locate it or open a different file use File > Open G-code"
            self.data.gcodeFile = ""
        
        try:
            #close the parent popup
            self.parentWidget.close()
        except AttributeError:
            pass #the parent popup does note exist to close
        
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
