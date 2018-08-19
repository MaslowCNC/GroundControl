import os
from kivy.uix.gridlayout import GridLayout
from UIElements.fileBrowser import FileBrowser
from kivy.uix.popup import Popup
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from UIElements.backgroundPickDlg import BackgroundPickDlg
from kivy.core.image import Image as CoreImage
from PIL import Image as PILImage
from io import BytesIO
import json

graphicsExtensions = (".jpg", ".png", ".jp2",".webp",".pbm",".ppm",".pgm")


class BackgroundMenu(GridLayout, MakesmithInitFuncs):

    def __init__(self, data, **kwargs):
        super(BackgroundMenu, self).__init__(**kwargs)
        self.data = data

    def updateAlignmentInConfig(self):
        self.data.config.set('Background Settings', 'manualReg',
                             self.data.backgroundManualReg)
        self.data.config.write()

    def openBackground(self):
        '''
        Open The Pop-up To Load A File
        Creates a new pop-up which can be used to open a file.
        '''
        # Starting path is either where the last opened file was
        # or the users home directory
        if not os.path.isdir(self.data.backgroundFile):
            startingPath = os.path.dirname(self.data.backgroundFile)
        else:
            # Don't go up a dir if the "backgroundFile" is a directory!
            startingPath = self.data.backgroundFile
        if startingPath is "":
            startingPath = os.path.expanduser('~')
        # We want to filter to show only files that ground control can open
        validFileTypes = graphicsExtensions
        validFileTypes = ['*{0}'.format(fileType) for fileType in validFileTypes]

        content = FileBrowser(select_string='Select',
                              favorites=[(startingPath, 'Last Location')], 
                              path=startingPath, 
                              filters=validFileTypes, dirselect=False)    
        content.bind(on_success=self.load, on_canceled=self.dismiss_popup,
                     on_submit=self.load)         
        self._popup = Popup(title="Select a file...", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def reloadBackground(self):
        self.processBackground()
        self.close()

    def processBackground(self):
        if self.data.backgroundFile == "" or os.path.isdir(
                                                self.data.backgroundFile):
            self.data.backgroundTexture = None
            self.data.backgroundManualReg = []
            self.updateAlignmentInConfig()
            self.data.backgroundRedraw = True
            return
        else:
            img = PILImage.open(self.data.backgroundFile)
            img.thumbnail((1920, 1080), PILImage.ANTIALIAS)
            img = img.transpose(PILImage.FLIP_TOP_BOTTOM)
            imgBytes = BytesIO()
            img.save(imgBytes, format="png")
            imgBytes.seek(0)
            texture = CoreImage(imgBytes, ext="png").texture
            self.data.backgroundTexture = texture
            if self.data.backgroundManualReg:
                # Already have centers to use; just go on to warp_image
                self.warp_image()
            else:
                # Start the manual alignment process
                self.realignBackground()

    def realignBackground(self):
        content = BackgroundPickDlg(self.data)
        content.setUpData(self.data)
        content.close = self.close_PickDlg
        self._popup = Popup(title="Background PointPicker", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def close_PickDlg(self, instance):
        if instance.accepted:
            # Update manual image registration marks
            self.data.backgroundManualReg = instance.tex_coords
            # Save the data from the popup
            self.updateAlignmentInConfig()
            self.warp_image()
        self.dismiss_popup()
        self.close()

    def warp_image(self):
        self.data.backgroundRedraw = True

    def clear_background(self):
        '''
        Clear background
        '''
        self.data.backgroundFile = ""
        self.processBackground()
        self.close()

    def load(self, instance):
        '''
        Load A Background Image File from the file dialog
        Takes in a file path (from the pop-up filepicker
        or directory, if no file was picked) and processes it.
        '''
        if len(instance.selection) == 1:
            filename = instance.selection[0]
        else:
            # User pressed Submit without picking a file
            filename = instance.path
        # Save the file in the config...
        self.data.backgroundFile = filename
        self.data.config.set('Background Settings',
                             'backgroundfile', str(self.data.backgroundFile))
        self.data.config.write()
        # close the open file popup
        self.dismiss_popup()
        # new image loaded so clear manual alignment centers
        self.data.backgroundManualReg = []
        # process it
        self.processBackground()   
        # Close the menu, going back to the main page.
        self.close()

    def dismiss_popup(self, *args):
        '''
        Close The File Picker (cancel was pressed instead of OK).
        '''
        self._popup.dismiss()
        pass
