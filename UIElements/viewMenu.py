from   kivy.uix.gridlayout                       import   GridLayout
from   UIElements.loadDialog                     import   LoadDialog
from   UIElements.pageableTextPopup              import   PageableTextPopup
from   kivy.uix.popup                            import   Popup
import re
from DataStructures.makesmithInitFuncs           import   MakesmithInitFuncs
from os                                          import   path
from Tkinter                                     import Tk
from tkFileDialog                                import   askopenfilename





class ViewMenu(GridLayout, MakesmithInitFuncs):

    page = 1
    
    def openFile(self):
        '''
        
        Open The Pop-up To Load A File
        
        Creates a new pop-up which can be used to open a file.
        
        '''
        
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        initialDir = path.dirname(self.data.gcodeFile)
        if initialDir is "": 
            initialDir = path.expanduser('~')
        validExtensions = self.data.config.get('Ground Control Settings', 'validExtensions').replace(",", "")
        filename = askopenfilename( initialdir = initialDir, filetypes = (("Gcode files", validExtensions),("all files","*.*")), title = "Open Gcode File") # show an "Open" dialog box and return the path to the selected file
        
        if filename is not None:
            self.data.gcodeFile = filename
            self.data.config.set('Maslow Settings', 'openFile', str(self.data.gcodeFile))
            self.data.config.write()
        
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
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self.page = 1
        self._popup.dismiss()
