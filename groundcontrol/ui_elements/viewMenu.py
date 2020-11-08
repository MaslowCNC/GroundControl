from   kivy.uix.gridlayout                       import   GridLayout
from   groundcontrol.ui_elements.fileBrowser                    import   FileBrowser
from   groundcontrol.ui_elements.pageableTextPopup              import   PageableTextPopup
from   kivy.uix.popup                            import   Popup
from groundcontrol.data_structures.makesmithInitFuncs           import MakesmithInitFuncs
from os                                          import    path





class ViewMenu(GridLayout, MakesmithInitFuncs):

    page = 1
    
    def openFile(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        #starting path is either where the last opened file was or the users home directory
        startingPath = path.dirname(self.data.gcodeFile)
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
    
    def clear_gcode(self):
        '''
        
        Clear gcode
        
        '''
        self.data.gcodeFile = ""
        
        #close the parent popup
        self.parentWidget.close()

    def reloadGcode(self):
        '''
        
        Trigger a reloading of the gcode file
        
        '''
        
        filePath = self.data.gcodeFile
        self.data.gcodeFile = ""
        self.data.gcodeFile = filePath
        
        #close the parent popup
        self.parentWidget.close()
    
    def load(self, instance):
        '''
        
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        
        try:        
            filename = instance.selection[0]
        except IndexError:
            print("must choose a file...")
        else:
            print(filename)
        
            #close the open file popup
            self.dismiss_popup()
        
            #locate the file
            self.data.gcodeFile = filename
            self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))

            #close the parent popup
            self.parentWidget.close()
    
    def resetView(self):
        '''
        
        Reset the gcode canvas view. Most of the work is done in the .kv file.
        
        '''
        #close the parent popup
        self.parentWidget.close()
    
    def clear_gcode(self):
        '''
        
        Reset the gcode canvas view. Most of the work is done in the .kv file.
        
        '''
        #locate the file
        self.data.gcodeFile = ""
        self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))

        #close the parent popup
        self.parentWidget.close()
    
    def show_gcode(self):
        '''
        
        Display the currently loaded gcode in a popup
        
        It would be cool if you could run the program stepping through using this popup
        
        '''
        
        popupText = ""
        titleString = "Gcode File"
        if len(self.data.gcode) is 0:
            popupText = "No gcode to display"
        else:
            if self.page<=1:
                line = 0
            else:
                line = (self.page-1)*447
                popupText = "...\n...\n...\n"

            if line>len(self.data.gcode):
                line = len(self.data.gcode)-447

            for lineNum, gcodeLine in enumerate(self.data.gcode):
                if lineNum>=line and lineNum<line+447:
                    popupText = popupText + str(lineNum+1) + ': ' + gcodeLine + "\n"
                elif lineNum>=line+447:
                    popupText = popupText + "...\n...\n...\n"
                    break
                
            titleString += ': ' + self.data.gcodeFile +'\nLines: '+str(line+1)+' - '+str(lineNum)+' of '+str(len(self.data.gcode))

        content = PageableTextPopup(cancel = self.dismiss_popup,
                                      prev = self.show_gcode_prev,
                                      next = self.show_gcode_next,
                                      text = popupText)

        self._popup = Popup(title=titleString, content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_gcode_next(self,*args):

        if (self.page)*447<len(self.data.gcode):
            self.page += 1
            self._popup.dismiss()
            self.show_gcode()

    def show_gcode_prev(self,*args):

        if self.page > 1:
            self.page -= 1
            self._popup.dismiss()
            self.show_gcode()
    
    def dismiss_popup(self, *args):
        '''
        
        Close The Pop-up
        
        '''
        self.page = 1
        self._popup.dismiss()
