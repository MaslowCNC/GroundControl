from   kivy.uix.gridlayout                       import   GridLayout
from   UIElements.loadDialog                     import   LoadDialog
from   UIElements.scrollableTextPopup            import   ScrollableTextPopup
from   kivy.uix.popup                            import   Popup
from kivy.uix.button                  import    Button
import re
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from os                                          import    path





class ViewMenu(GridLayout, MakesmithInitFuncs):

    page = 1
    
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
    
    def load(self, filePath, filename):
        '''
        
        Load A File (Any Type)
        
        Takes in a file path (from pop-up) and handles the file appropriately for the given file-type.
        
        '''
        
        #close the open file popup
        self.dismiss_popup()
        
        #locate the file
        filename = filename[0]
        fileExtension = path.splitext(filename)[1]
        
        validExtensions = self.data.config.get('Ground Control Settings', 'validExtensions').replace(" ", "").split(',')
        
        if fileExtension in validExtensions:
            self.data.gcodeFile = filename
            self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))
            self.data.config.write()
        else:
            self.data.message_queue.put("Message: Ground control can only open gcode files with extensions: " + self.data.config.get('Ground Control Settings', 'validExtensions'))
        
        #close the parent popup
        self.parentWidget.close()
    
    def resetView(self):
        '''
        
        Reset the gcode canvas view. Most of the work is done in the .kv file.
        
        '''
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
            if self.page<=1:
                line = 0
            else:
                line = (self.page-1)*447
                popupText = "...\n...\n...\n"

            if line>len(self.data.gcode):
                line = len(self.data.gcode)-447

            for lineNum, gcodeLine in enumerate(self.data.gcode):
                if lineNum>=line and lineNum<line+447:
                    popupText = popupText + gcodeLine + "\n"
                elif lineNum>=line+447:
                    popupText = popupText + "...\n...\n...\n"
                    break
                
        content = ScrollableTextPopup(cancel = self.dismiss_popup,
                                      prev = self.show_gcode_prev,
                                      next = self.show_gcode_next,
                                      text = popupText)

        titleString = 'Gcode File: ' + self.data.gcodeFile +'\nLines: '+str(line+1)+' - '+str(lineNum)+' of '+str(len(self.data.gcode))
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
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self.page = 1
        self._popup.dismiss()
