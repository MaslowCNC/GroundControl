from kivy.uix.gridlayout         import   GridLayout
from UIElements.loadDialog       import   LoadDialog
from kivy.uix.popup              import   Popup



class ViewMenu(GridLayout):
    gcodeFilePath = ""
    
    def openFile(self):
        '''
        
        Open A File
        
        '''
        self.show_load()
    
    def setGcodeLocation(self,gcodeLocation):
        self.gcodeCanvas = gcodeLocation
        
        #self.gcodeCanvas.gcode = ["G01 X10", "G02 X Y I J"]
        #gcodeLocation.updateGcode()
    
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
        from kivy.uix.popup import Popup
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
        #This reloads the gcode from the hard drive in case it has been updated.
        try:
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

            self.gcodeCanvas.gcode = filtersparsed
            filterfile.close() #closes the filter save file
        except:
            if filename is not "":
                print "Cannot reopen gcode file. It may have been moved or deleted. To locate it or open a different file use File > Open G-code"
            self.gcodeFilePath = ""
        self.gcodeCanvas.updateGcode()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()
