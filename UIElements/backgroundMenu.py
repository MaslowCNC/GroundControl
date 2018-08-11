from kivy.uix.gridlayout                       import   GridLayout
from UIElements.fileBrowser                    import   FileBrowser
from kivy.uix.popup                            import   Popup
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from UIElements.BackgroundPickDlg                import BackgroundPickDlg
from UIElements.BackgroundSettingsDlg            import BackgroundSettingsDlg
import os
import cv2
import numpy as np
import json

graphicsExtensions = (".jpg", ".png", ".jp2",".webp",".pbm",".ppm",".pgm")


class BackgroundMenu(GridLayout, MakesmithInitFuncs):

    def __init__(self, data, **kwargs):
        super(BackgroundMenu, self).__init__(**kwargs)
        self.data = data

    def updateAlignmentInConfig(self):
        self.data.config.set('Background Settings', 'manualReg',
                             json.dumps(self.data.backgroundManualReg))
        self.data.config.set('Background Settings', 'alignment',
                             json.dumps(self.data.backgroundAlignment))
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
            self.data.backgroundImage = None
            self.data.backgroundManualReg = []
            self.data.gcodeRedraw = True
            return
        else:
            self.data.originalimage = cv2.imread(self.data.backgroundFile)
            self.data.backgroundImage = self.data.originalimage
            if self.data.backgroundManualReg:
                # Already have centers to use; just go on to warp_image
                self.warp_image()
            else:
                # Start the manual alignment process
                self.realignBackground()

    def realignBackground(self):
        self.data.backgroundImage = self.data.originalimage.copy()
        content = BackgroundPickDlg(self.data)
        content.setUpData(self.data)
        content.close = self.close_PickDlg
        self._popup = Popup(title="Background PointPicker", content=content,
                            size_hint=(1.0, 1.0))
        self._popup.open()

    def close_PickDlg(self, instance):
        if instance.centers:
            # Update manual image registration marks
            self.data.backgroundManualReg = instance.centers
            # Save the data from the popup
            self.updateAlignmentInConfig()
            self.warp_image()
        self.dismiss_popup()
        self.close()

    def warp_image(self):
        # Load into locals for shorthand
        # this skew correction is similar to gcodeCanvas.py
        centers = self.data.backgroundManualReg
        if len(centers) == 4:
            TL = self.data.backgroundAlignment[0]
            TR = self.data.backgroundAlignment[1]
            BL = self.data.backgroundAlignment[2]
            BR = self.data.backgroundAlignment[3]
            # Handle skew in output coordinates
            leftmost = min(TL[0], BL[0])
            rightmost = max(TR[0], BR[0])
            topmost = max(TL[1], TR[1])
            botmost = min(BL[1], BR[1])
            h = topmost - botmost
            w = rightmost - leftmost
            # Construct transformation matrices
            pts1 = np.float32([centers[0], centers[1], centers[2], centers[3]])
            pts2 = np.float32(
                [[TL[0]-leftmost, TL[1]-botmost], [TR[0]-leftmost, TR[1]-botmost],
                 [BL[0]-leftmost, BL[1]-botmost], [BR[0]-leftmost, BR[1]-botmost]]) 
            M = cv2.getPerspectiveTransform(pts1, pts2) 
            self.data.backgroundImage = cv2.warpPerspective(
                                        self.data.backgroundImage, M, (w, h))            
        # Trigger a redraw
        self.data.gcodeRedraw = True

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

    def openBackgroundSettings(self):
        '''
        Open the background settings page
        '''
        content = BackgroundSettingsDlg(self.data)
        content.setUpData(self.data)
        content.close = self.closeBackgroundSettings
        self._popup = Popup(title="Background Settings", content=content,
                            size_hint=(0.5, 0.5))
        self._popup.open()

    def closeBackgroundSettings(self, instance):
        self.updateAlignmentInConfig()
        self.reloadBackground()
        self._popup.dismiss()

    def dismiss_popup(self, *args):
        '''
        Close The File Picker (cancel was pressed instead of OK).
        '''
        self._popup.dismiss()
        pass
