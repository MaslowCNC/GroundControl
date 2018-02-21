from   kivy.uix.gridlayout                       import   GridLayout
from   UIElements.fileBrowser                    import   FileBrowser
from   UIElements.pageableTextPopup              import   PageableTextPopup
from   kivy.uix.popup                            import   Popup
from   kivy.clock                                import   Clock

from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from UIElements.BackgroundPickDlg                import BackgroundPickDlg
from UIElements.BackgroundSettingsDlg            import BackgroundSettingsDlg
import os
import cv2
import numpy as np
import json

graphicsExtensions = (".jpg", ".png", ".jp2",".webp",".pbm",".ppm",".pgm")




class BackgroundMenu(GridLayout, MakesmithInitFuncs):
    
    backgroundFile = ""
    backgroundTLHSV = None
    backgroundTRHSV = None
    backgroundBLHSV = None
    backgroundBRHSV = None
    
    
    def __init__(self, data, **kwargs):
        super(BackgroundMenu, self).__init__(**kwargs)
        self.data = data
        
        #Load the data from the config file 
        self.backgroundFile = self.data.config.get('Background Settings', 'backgroundFile')
        self.backgroundTLHSV = json.loads(self.data.config.get('Background Settings', 'backgroundTLHSV'))
        self.backgroundTRHSV = json.loads(self.data.config.get('Background Settings', 'backgroundTRHSV'))
        self.backgroundBLHSV = json.loads(self.data.config.get('Background Settings', 'backgroundBLHSV'))
        self.backgroundBRHSV = json.loads(self.data.config.get('Background Settings', 'backgroundBRHSV'))
        self.data.backgroundTLPOS = json.loads(self.data.config.get('Background Settings', 'backgroundTLPOS'))
        self.data.backgroundTRPOS = json.loads(self.data.config.get('Background Settings', 'backgroundTRPOS'))
        self.data.backgroundBLPOS = json.loads(self.data.config.get('Background Settings', 'backgroundBLPOS'))
        self.data.backgroundBRPOS = json.loads(self.data.config.get('Background Settings', 'backgroundBRPOS'))


        #Fire off a clock to check for new images every 2 seconds - this should only run once per app start!
        if self.data.backgroundClock is None:
            self.data.backgroundClock=Clock.schedule_interval(self.timer, 2)

    def findHSVcenter(self, img, hsv, hsvLow, hsvHi, bbtl, bbbr, clean=3, minarea=1000, maxarea=6000, tag="A"):
        if isinstance(hsvLow, list):
            #cv2 can't handle lists... make 'em into tuples
            hsvLow = tuple(hsvLow)
            hsvHi = tuple(hsvHi)
            
        #Mask to find the blobs
        if hsvLow[0] > hsvHi[0]:
            #It's wrapped [red]
            bottom = (0, hsvLow[1], hsvLow[2])
            maska=cv2.inRange(hsv, bottom,hsvHi)

            top = (180, hsvHi[1], hsvHi[2])
            maskb=cv2.inRange(hsv, hsvLow, top)
            mask=cv2.bitwise_or(maska, maskb)
        else:
            mask=cv2.inRange(hsv, hsvLow, hsvHi)

        #erode-dilate to clean up noise
        mask = cv2.erode(mask, None, iterations=clean)
        mask = cv2.dilate(mask, None, iterations=clean)

        #find contours
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        
        #If we found some, lets check their size and location to pick the best ones
        if len(cnts) > 0:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)  #Sort so we find biggest first.
            for c in cnts:
                if cv2.contourArea(c) >= minarea and cv2.contourArea(c)<=maxarea:                    #Discriminate based on size
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))   #ToDo - why not use the XY above?
                    if center[0] >= bbtl[0] and center[0] <= bbbr[0]  and center[1] >= bbtl[1] and center[1] <= bbbr[1]:
                        #Mark the image
                        cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 5)
                        cv2.circle(img, center, 5, (0, 0, 255), -1)
                        return center
        return center
        
    def openBackground(self):
        '''
        Open The Pop-up To Load A File
        Creates a new pop-up which can be used to open a file.
        '''
        self.backgroundFile = self.data.config.get('Background Settings', 'backgroundFile')

        #starting path is either where the last opened file was or the users home directory
        if not os.path.isdir(self.backgroundFile):
            startingPath = os.path.dirname(self.backgroundFile)
        else:
            startingPath = self.backgroundFile #Don't go up a dir if the "backgroundFile" is a directory!

        print "SP:["+startingPath+"]"

        if startingPath is "": 
            startingPath = os.path.expanduser('~')
                
        #We want to filter to show only files that ground control can open
        validFileTypes = graphicsExtensions
        validFileTypes = ['*{0}'.format(fileType) for fileType in validFileTypes] #add a '*' to each one to match the format the widget expects
        
        content = FileBrowser(select_string='Select', 
                    favorites=[(startingPath, 'Last Location')], 
                    path = startingPath, 
                    filters = validFileTypes, dirselect=False)
                    
        content.bind(on_success=self.load,
                         on_canceled=self.dismiss_popup,
                         on_submit=self.load)
                    
        self._popup = Popup(title="Select a file, or no file picks ""Latest File"" in this directory...", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        
    def reloadBackground(self):
        print "Reload: ["+self.backgroundFile+"]" #ToD: This aways shows up empty?

        self.processBackground()
        self.close()
    
    def timer(self, *args):
        if self.doesNewFileExist():
            self.processBackground()
 
    def doesNewFileExist(self, *args):
        print "Tick: ["+self.backgroundFile+"]"
        if self.backgroundFile=="":
            return False
        
        file=self.backgroundFile

        #If file is a directory, then "load the latest from that directory"
        if not os.path.isdir(file):
            return False #I'm not going to automatically reload the same file
        else:
            files = os.listdir(file)
            filelst =[]
            for afile in files:
                if afile.lower().endswith(graphicsExtensions):
                    filelst.append(os.path.join(file,afile))
            filelst.sort(key=os.path.getmtime, reverse=True)

            if len(filelst) == 0:
                file=None
                return

            file = filelst[0]
            return file <> self.backgroundLastFile

    def processBackground(self):
        if self.backgroundFile=="":
            print "NoBackgroundfile"
            self.data.backgroundImage = None
            self.data.gcodeRedraw=True
        else:
            print "ProcessBackground: ["+self.backgroundFile+"]"
            file=self.backgroundFile
            
            #If file is a directory, then "load the latest from that directory"
            if os.path.isdir(file):
                files = os.listdir(file)
                filelst =[]
                for afile in files:
                    if afile.lower().endswith(graphicsExtensions):
                        filelst.append(os.path.join(file,afile))
                
                if len(filelst) == 0:
                    file=None
                    return
                    
                filelst.sort(key=os.path.getmtime, reverse=True)
                file = filelst[0]

                #Save the file we're processing...
                self.backgroundLastFile = file
                
            img = cv2.imread(file)
            self.data.originalimage=img.copy()
            hsv = hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    #HSV colorspace is easier to do "Color" than RGB
            xmax=img.shape[1]
            ymax=img.shape[0]
            xmid = xmax/2
            ymid = ymax/2;

            #Find the centers of the markers:
            centers = []
            
            if not isinstance(self.backgroundTLHSV,list) and not isinstance(self.backgroundTLHSV, tuple):
                #Not a valid tuple or list, consider it a flag to go to manual mode immediately
                centers.append(None)
            else:
                centers.append(self.findHSVcenter(img, hsv, self.backgroundTLHSV[0], self.backgroundTLHSV[1], (0,0), (xmid,ymid), tag="A"))
                centers.append(self.findHSVcenter(img, hsv, self.backgroundTRHSV[0], self.backgroundTRHSV[1], (xmid,0),(xmax, ymid), tag="B"))
                centers.append(self.findHSVcenter(img, hsv, self.backgroundBLHSV[0], self.backgroundBLHSV[1], (0,ymid), (xmid, ymax), tag="C"))
                centers.append(self.findHSVcenter(img, hsv, self.backgroundBRHSV[0], self.backgroundBRHSV[1], (xmid,ymid), (xmax, ymax), tag="D"))
            
            self.data.backgroundImage = img
            if None in centers:
                self.realignBackground()
            else:
                #We have all points; just go on to warp_image
                self.centers=centers
                self.warp_image()
                
    def realignBackground(self):
        self.data.backgroundImage=self.data.originalimage.copy() #Reload original image
        content = BackgroundPickDlg(self.data)
        content.setUpData(self.data)
        content.close = self.close_PickDlg
        self._popup = Popup(title="Background PointPicker", content=content, size_hint = (0.9,0.9))
        self._popup.open()

    def close_PickDlg(self, instance):
        self.centers=instance.centers   #Grab the data
        self.dismiss_popup()            #Close pointpicker dialog
        self.warp_image()               #Process with the user-picked centers
        self.close()                    #Close background menu dialog
        
    def warp_image(self):
        #Load into locals for shorthand... this skew correction is similar to gcodeCanvas.py
        centers=self.centers
        if len(centers)==4:
            TL=self.data.backgroundTLPOS
            TR=self.data.backgroundTRPOS
            BL=self.data.backgroundBLPOS
            BR=self.data.backgroundBRPOS

            #Handle skew in output coordinates
            leftmost = min(TL[0],BL[0])
            rightmost=max(TR[0],BR[0])
            topmost=max(TL[1],TR[1])
            botmost=min(BL[1],BR[1])
            h = topmost-botmost
            w = rightmost-leftmost

            #Construct transformation matrices
            pts1 = np.float32([centers[0],centers[1],centers[2],centers[3]])
            pts2 = np.float32(
                [[TL[0]-leftmost,TL[1]-botmost],[TR[0]-leftmost, TR[1]-botmost],
                 [BL[0]-leftmost,BL[1]-botmost],[BR[0]-leftmost,BR[1]-botmost]]) 
            
            M = cv2.getPerspectiveTransform(pts1,pts2)
            
            self.data.backgroundImage = cv2.warpPerspective(self.data.backgroundImage,M,(w,h))
                
        #Trigger a redraw
        self.data.gcodeRedraw=True
        
    def clear_background(self):
        '''
        Clear background
        '''
        print "Clear"
        self.backgroundFile=""
        self.processBackground()
        self.close()
        
    def load(self, instance):
        '''
        Load A Background Image File from the file dialog
        Takes in a file path (from the pop-up filepicker) (or directory, if no file picked) and processes it.
        '''
        if len(instance.selection)==1:
            filename = instance.selection[0]
        else:
            filename = instance.path    #User pressed Submit without picking a file, indicating "newest in this dir"

        #Save the file in the config...
        self.backgroundFile = filename
        self.data.config.set('Background Settings', 'openFile', str(self.backgroundFile))
        self.data.config.write()
        print "Open: ["+self.backgroundFile+"]"
        
        #close the open file popup
        self.dismiss_popup()
        
        #process it
        self.processBackground()
        
        #Close the menu, going back to the main page.
        self.close()
    
    def openBackgroundSettings(self):
        '''
        Open the background settings page
        '''
        content = BackgroundSettingsDlg(self)
        content.close = self.closeBackgroundSettings
        self._popup = Popup(title="Background Settings", content=content, size_hint = (0.6,0.5))
        self._popup.open()
        
    def closeBackgroundSettings(self, instance):
        #Convert string data back into lists for use (should be a list of tuples, but I fixed it so it can be a list of lists)...
        self.backgroundTLHSV =json.loads(instance.backgroundTLHSV)
        self.backgroundTRHSV =json.loads(instance.backgroundTRHSV)
        self.backgroundBLHSV =json.loads(instance.backgroundBLHSV)
        self.backgroundBRHSV =json.loads(instance.backgroundBRHSV)
        self.data.backgroundTLPOS =json.loads(instance.backgroundTLPOS)
        self.data.backgroundTRPOS =json.loads(instance.backgroundTRPOS)
        self.data.backgroundBLPOS =json.loads(instance.backgroundBLPOS)
        self.data.backgroundBRPOS =json.loads(instance.backgroundBRPOS)

        #Write the data to the config file (just use the json data)
        self.data.config.set('Background Settings', 'backgroundTLHSV', instance.backgroundTLHSV)
        self.data.config.set('Background Settings', 'backgroundTRHSV', instance.backgroundTRHSV)
        self.data.config.set('Background Settings', 'backgroundBLHSV', instance.backgroundBLHSV)
        self.data.config.set('Background Settings', 'backgroundBRHSV', instance.backgroundBRHSV)
        self.data.config.set('Background Settings', 'backgroundTLPOS', instance.backgroundTLPOS)
        self.data.config.set('Background Settings', 'backgroundTRPOS', instance.backgroundTRPOS)
        self.data.config.set('Background Settings', 'backgroundBLPOS', instance.backgroundBLPOS)
        self.data.config.set('Background Settings', 'backgroundBRPOS', instance.backgroundBRPOS)        
        self.data.config.write()
        self._popup.dismiss()   #Close the settings popup
        
    
    def dismiss_popup(self, *args):
        '''
        Close The File Picker (cancel was pressed instead of OK).
        '''
        self._popup.dismiss()
        pass #And take no other action...
