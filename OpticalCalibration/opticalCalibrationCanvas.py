from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty, BooleanProperty
from kivy.graphics                           import Color, Ellipse, Line
from kivy.graphics.texture                   import Texture
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from kivy.graphics.transformation            import Matrix
from kivy.clock                              import Clock
from kivy.uix.image                          import Image
from kivy.app                                import App
from kivy.uix.popup                          import Popup
from kivy.uix.label                          import Label

from OpticalCalibration.cameraCenterCalibration import calculateCenterOfArc
from UIElements.notificationPopup            import NotificationPopup
from Settings                                import maslowSettings
from functools                               import partial
from scipy.spatial                           import distance as dist
from imutils                                 import perspective
from imutils                                 import contours
import numpy                                 as np
import imutils
import cv2
import time
import re
import math
import sys
import global_variables

class KivyCamera(Image):
    def __init__(self, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = None

    def start(self, capture, fps=30):
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def stop(self):
        Clock.unschedule_interval(self.update)
        self.capture = None

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tostring()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

    def getCapture(self):
        return self.capture.read()

#capture = None

class MeasuredImage(Image):
    def __init__(self, **kwargs):
        super(MeasuredImage, self).__init__(**kwargs)

    def update(self, frame):
        cv2.imwrite("measuredImage.png",frame)
        buf1 = cv2.flip(frame,0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture

class OpticalCalibrationCanvas(GridLayout):

    capture = None
    cameraCount = 0
    refObj = None
    D = 1
    xD = 1
    yD = 1
    done = ObjectProperty(None)
    currentX, currentY = 0, 0
    calX = 0
    calY = 0
    matrixSize = (31, 15)
    calErrorsX = np.zeros(matrixSize)
    calErrorsY = np.zeros(matrixSize)
    measuredErrorsX = np.zeros(matrixSize)
    measuredErrorsY = np.zeros(matrixSize)
    cameraCenteringPoints = []
    opticalCenter = (None, None)

    presets = [ ["48x36 Top Left", [-15 , 7] , [0, 0] ],
                ["48x36 Bottom Left", [0, 7] , [15, 0] ],
                ["48x36 Top Right", [-15 , 0] , [0, -7] ],
                ["48x36 Bottom Right", [0, 0] , [15, -7] ],
                ["96x48 Full Area", [-15, 7] , [15, -7] ],
                ["8.5x11 (Portrait)", [-1, 1] , [1, -2] ],
                ["11x17 (Portrait)", [-1, 2] , [2, -3] ],
               ]

    #values: ["48x36 Top Left", "48x36 Bottom Left", "48x36 Top Right", "48x36 Bottom Right", "96x48 Full Area", "8.5x11 (Portait)","11x17 (Portrait)"]

    markerWidth = 0.5*25.4
    markerX = 0.5*25.4
    markerY = 0.5*25.4
    inAutoMode = False
    inMesureOnlyMode = False
    HomingScanDirection = 1
    HomingX = 0.0
    HomingY = 0.0
    HomingPosX = 0
    HomingPosY = 0
    HomingRange = 4
    HomingTLX = -2
    HomingTLY = +2
    HomingBRX = +2
    HomingBRY = -2
    counter =0
    bedHeight = 48*25.4
    bedWidth = 96*25.4
    xCurve = np.zeros(shape=(6))  # coefficients for quadratic curve
    yCurve = np.zeros(shape=(6))  # coefficients for quadratic curve

    #def initialize(self):

    def initialize(self):
        xyErrors = self.data.config.get('Computed Settings', 'xyErrorArray')
        self.calErrorsX, self.calErrorsY = maslowSettings.parseErrorArray(xyErrors, True)
        self.bedHeight = float(self.data.config.get('Maslow Settings', 'bedHeight'))
        self.bedWidth = float(self.data.config.get('Maslow Settings', 'bedWidth'))

        #print str(xErrors[2][0])

        # Work backwards to find a camera (assumes <= 2 cameras)
        for i in reversed(range(2)):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cameraCount = i + 1
                cap.release()
                break
            cap.release()

        print "Found %d cameras" % self.cameraCount
        self.ids.cameras.values = self.cameras()
        self.startCamera(self.cameraCount - 1)

        self.inAutoMode = False
        self.inMeasureOnlyMode = False

        mat = Matrix().scale(.2, .2, 1)
        self.ids.opticalScatter.apply_transform(mat, (0,0))
        moveVertical = self.bedHeight/2
        moveHorizontal = self.bedWidth/2
        mat = Matrix().translate(moveHorizontal, moveVertical, 0)
        self.ids.opticalScatter.apply_transform(mat)
        self.drawCalibration()
        self.ids.topLeftX.text = str(self.HomingTLX)
        self.ids.topLeftY.text = str(self.HomingTLY)
        self.ids.bottomRightX.text = str(self.HomingBRX)
        self.ids.bottomRightY.text = str(self.HomingBRY)
        self.ids.markerX.text = str(round(self.markerX/25.4,3))
        self.ids.markerY.text = str(round(self.markerY/25.4,3))

    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        self.inAutoMode = False
        self.inMeasureOnlyMode = False


    def startCamera(self, index):
        print "Selected Camera Index:"+str(index)
        self.capture = cv2.VideoCapture(index)
        if self.capture.isOpened():
            self.ids.KivyCamera.start(self.capture)
        else:
            print "Failed to open camera"

    def cameras(self):
        return ["%d" % i for i in range(self.cameraCount)]

    def setCamera(self, val):
        self.capture.release()
        self.startCamera(int(val))

    def on_stop(self):
        self.capture.release()

    def on_UpdateTopLeftX(self,value=[0,False]):
        if (value[1]==False):
            try:
                _tlX=int(self.ids.topLeftX.text)
                self.ids.topLeftX.text = str(_tlX)
                self.HomingTLX = _tlX
            except:
                print "Value not int"
                self.ids.topLeftX.text = ""

    def on_UpdateTopLeftY(self,value=[0,False]):
        if (value[1]==False):
            try:
                _tlY=int(self.ids.topLeftY.text)
                self.ids.topLeftY.text = str(_tlY)
                self.HomingTLY = _tlY
            except:
                print "Value not int"
                self.ids.topLeftY.text = ""

    def on_UpdateBottomRightX(self,value=[0,False]):
        if (value[1]==False):
            try:
                _brX=int(self.ids.bottomRightX.text)
                self.ids.bottomRightX.text = str(_brX)
                self.HomingBRX = _brX
            except:
                print "Value not int"
                self.ids.bottomRightX.text = ""

    def on_UpdateBottomRightY(self,value=[0,False]):
        if (value[1]==False):
            try:
                _brY=int(self.ids.bottomRightY.text)
                self.ids.bottomRightY.text = str(_brY)
                self.HomingBRY = _brY
            except:
                print "Value not int"
                self.ids.bottomRightY.text = ""

    def on_UpdateMarkerX(self,value=[0,False]):
        if (value[1]==False):
            try:
                _mX=float(self.ids.markerX.text)
                self.ids.markerX.text = str(round(_mX,3))
                self.markerX = _mX*25.4
            except:
                print "Value not float"
                self.ids.markerX.text = ""

    def on_UpdateMarkerY(self,value=[0,False]):
        if (value[1]==False):
            try:
                _mY=float(self.ids.markerY.text)
                self.ids.markerY.text = str(round(_mY,3))
                self.markerY = _mY*25.4
            except:
                print "Value not float"
                self.ids.markerY.text = ""





    def on_SaveCSV(self):
        outFile = open("calibrationValues.csv","w")
        line = ""
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.calErrorsX[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.write("\n")
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.calErrorsY[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.close()
        outFile = open("measurementValues.csv","w")
        line = ""
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.measuredErrorsX[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.write("\n")
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.measuredErrorsY[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.close()

    def on_Preset(self, preset):
        for _preset in self.presets:
            if preset == _preset[0]:
                self.ids.topLeftX.text = str(_preset[1][0])
                self.ids.topLeftY.text = str(_preset[1][1])
                self.ids.bottomRightX.text = str(_preset[2][0])
                self.ids.bottomRightY.text = str(_preset[2][1])
                self.HomingTLX = _preset[1][0]
                self.HomingTLY = _preset[1][1]
                self.HomingBRX = _preset[2][0]
                self.HomingBRY = _preset[2][1]



    def midpoint(self, ptA, ptB):
        return ((ptA[0]+ptB[0])*0.5, (ptA[1]+ptB[1])*0.5)

    def do_Exit(self):
        if self.capture != None:
            self.capture.release()
            self.capture = None
            self.parent.parent.parent.dismiss()

    def translatePoint(self, xB, yB, xA, yA, angle):
        cosa = math.cos((angle)*3.141592/180.0)
        sina = math.sin((angle)*3.141592/180.0)
        xB -= xA
        yB -= yA
        _xB = xB*cosa - yB*sina
        _yB = xB*sina + yB*cosa
        xB = _xB+xA
        yB = _yB+yA
        return xB, yB

    def simplifyContour(self,c,sides=4):
        tolerance = 0.01
        while True:
            _c = cv2.approxPolyDP(c, tolerance*cv2.arcLength(c,True), True)
            if len(_c)<=sides or tolerance>0.5:
                break
            tolerance += 0.01
        if len(_c)<sides:# went too small.. now lower the tolerance until four points or more are reached
            while True:
                tolerance -= 0.01
                _c = cv2.approxPolyDP(c, tolerance*cv2.arcLength(c,True), True)
                if len(_c)>=sides or tolerance <= 0.1:
                    break
    #    print "len:"+str(len(c))+", tolerance:"+str(tolerance)
        return _c #_c is the smallest approximation we can find with four our more

    def drawCalibration(self):
        self.ids.opticalScatter.canvas.clear()
        for y in range(7, -8, -1):
            points = []
            for x in range(-15, 16, +1):
                points.append(x*3*25.4+self.bedWidth/2.0)
                points.append(y*3*25.4+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(0,0,1)
                Line(points=points)

        for x in range(-15, 16, +1):
            points = []
            for y in range(7, -8, -1):
                points.append(x*3*25.4+self.bedWidth/2.0)
                points.append(y*3*25.4+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(0,0,1)
                Line(points=points)

        for y in range(7, -8, -1):
            points = []
            for x in range(-15, 16, +1):
                if (self.inMeasureOnlyMode):
                    points.append(x*3*25.4-self.measuredErrorsX[x+15][7-y]+self.bedWidth/2.0)
                    points.append(y*3*25.4-self.measuredErrorsY[x+15][7-y]+self.bedHeight/2.0)
                else:
                    points.append(x*3*25.4-self.calErrorsX[x+15][7-y]+self.bedWidth/2.0)
                    points.append(y*3*25.4-self.calErrorsY[x+15][7-y]+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(1,0,0)
                Line(points=points)

        for x in range(-15, 16, +1):
            points = []
            for y in range(7, -8, -1):
                if (self.inMeasureOnlyMode):
                    points.append(x*3*25.4-self.measuredErrorsX[x+15][7-y]+self.bedWidth/2.0)
                    points.append(y*3*25.4-self.measuredErrorsY[x+15][7-y]+self.bedHeight/2.0)
                else:
                    points.append(x*3*25.4-self.calErrorsX[x+15][7-y]+self.bedWidth/2.0)
                    points.append(y*3*25.4-self.calErrorsY[x+15][7-y]+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(1,0,0)
                Line(points=points)

        for y in range(7, -8, -1):
            points = []
            for x in range(-15, 16, +1):
                points.append(x*3*25.4-self.calSurface(x*3*25.4,y*3*25.4,0)+self.bedWidth/2.0)
                points.append(y*3*25.4-self.calSurface(x*3*25.4,y*3*25.4,1)+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(0,1,0)
                Line(points=points)

        for x in range(-15, 16, +1):
            points = []
            for y in range(7, -8, -1):
                points.append(x*3*25.4-self.calSurface(x*3*25.4,y*3*25.4,0)+self.bedWidth/2.0)
                points.append(y*3*25.4-self.calSurface(x*3*25.4,y*3*25.4,1)+self.bedHeight/2.0)
            with self.ids.opticalScatter.canvas:
                Color(0,1,0)
                Line(points=points)


    def calSurface(self,x,y,plane):
        if plane == 0:
            retVal = self.xCurve[4]*x**2.0 + self.xCurve[5]*y**2.0 + self.xCurve[3]*x*y + self.xCurve[1]*x + self.xCurve[2]*y + self.xCurve[0]
        else:
            retVal = self.yCurve[4]*x**2.0 + self.yCurve[5]*y**2.0 + self.yCurve[3]*x*y + self.yCurve[1]*x + self.yCurve[2]*y + self.yCurve[0]
        return retVal


    def on_touch_up(self, touch):

        if touch.is_mouse_scrolling:
            self.zoomCanvas(touch)

    def zoomCanvas(self, touch):
        if touch.is_mouse_scrolling:
            scaleFactor = .1
            if touch.button == 'scrollup':
                mat = Matrix().scale(1-scaleFactor, 1-scaleFactor, 1)
                self.ids.opticalScatter.apply_transform(mat, anchor = touch.pos)
            elif touch.button == 'scrolldown':
                mat = Matrix().scale(1+scaleFactor, 1+scaleFactor, 1)
                self.ids.opticalScatter.apply_transform(mat, anchor = touch.pos)


    def updateScreenValues(self, curX = -20, curY = -20):
        self.ids.OpticalCalibrationDistance.text = " pixels\mm: {:.3f}\n".format(self.D)#Cal Error({:.3f},{:.3f})\n".format(self.D, self.calX, self.calY)
        calX = 0
        calY = 0
        count = 0
        reColor = False
        #print str(self.HomingTLX)+", "+str(self.HomingBRX)+", "+str(self.HomingTLY)+", "+str(self.HomingBRY)
        for y in range(self.HomingTLY, self.HomingBRY - 1, -1):
            for x in range(self.HomingTLX, self.HomingBRX + 1, +1):
                #if (abs(y)<=7)
                if ((y == curY) and (x == curX) ):
                    reColor = True
                    self.ids.OpticalCalibrationDistance.text += "[color=ff3333]"
                if (self.inMeasureOnlyMode):
                    self.ids.OpticalCalibrationDistance.text += "[{:.2f},{:.2f}] ".format(self.measuredErrorsX[x+15][7-y], self.measuredErrorsY[x+15][7-y])
                    calX += (self.measuredErrorsX[x+15][7-y]-self.measuredErrorsX[15][7]) ** 2.0
                    calY += (self.measuredErrorsY[x+15][7-y]-self.measuredErrorsY[15][7]) ** 2.0
                else:
                    self.ids.OpticalCalibrationDistance.text += "[{:.2f},{:.2f}] ".format(self.calErrorsX[x+15][7-y], self.calErrorsY[x+15][7-y])
                    calX += (self.measuredErrorsX[x+15][7-y]-self.measuredErrorsX[15][7]) ** 2.0
                    calY += (self.measuredErrorsY[x+15][7-y]-self.measuredErrorsY[15][7]) ** 2.0

                if reColor:
                    reColor = False
                    self.ids.OpticalCalibrationDistance.text += "[/color]"
                count += 1
                #print count
            self.ids.OpticalCalibrationDistance.text +="\n"
        calX = math.sqrt(calX/count)
        calY = math.sqrt(calY/count)
        self.ids.OpticalCalibrationDistance.text += "X,Y Offset RMS: {:.3f}, {:.3f}\n".format(calX,calY)
        self.drawCalibration()





    def removeOutliersAndAverage(self, data):
        mean = np.mean(data)
        print "mean:"+str(mean)
        sd = np.std(data)
        print "sd:"+str(sd)
        tArray = [x for x in data if ( (x >= mean-2.0*sd) and (x<=mean+2.0*sd))]
        return np.average(tArray), np.std(tArray)


    def on_SaveAndSend(self):
        _str = ""
        _strcomma = ""
        for z in range(2):
            for y in range(15):
                for x in range(31):
                    if ((x==30) and (y==14) and (z==1)):
                        _strcomma = ""
                    else:
                        _strcomma = ","
                    if (z==0):
                        _str += str(int(self.calErrorsX[x][y]*1000))+_strcomma
                    else:
                        _str += str(int(self.calErrorsY[x][y]*1000))+_strcomma
        #print _str

        App.get_running_app().data.config.set('Computed Settings', 'calX0', str(float(round(xCurve[0],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calX1', str(float(round(xCurve[1],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calX2', str(float(round(xCurve[2],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calX3', str(float(round(xCurve[3],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calX4', str(float(round(xCurve[4],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calX5', str(float(round(xCurve[5],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY0', str(float(round(yCurve[0],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY1', str(float(round(yCurve[1],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY2', str(float(round(yCurve[2],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY3', str(float(round(yCurve[3],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY4', str(float(round(yCurve[4],4))))
        App.get_running_app().data.config.set('Computed Settings', 'calY5', str(float(round(yCurve[5],4))))

        App.get_running_app().data.config.set('Computed Settings', 'xyErrorArray', _str)

    def on_WipeController(self):
        self.data.gcode_queue.put("$RST=^ ")

    def on_ReturnToCenter(self):
        print "Moving to:[0, 0]"
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G91  ")

    def on_AutoHome(self, measureMode = False):

        minX = self.HomingTLX
        maxX = self.HomingBRX
        minY = self.HomingTLY
        maxY = self.HomingBRY

        if measureMode == True:
            print "Measure Only"
            self.inMeasureOnlyMode = True
        #print "Measure:"+str(self.inMeasureOnlyMode)
        if self.inAutoMode == False:
            self.HomingX = 0.0
            self.HomingY = 0.0
            self.HomingPosX = minX
            self.HomingPosY = minY
            self.HomingScanDirection = 1
            self.inAutoMode = True
        else:
            # note, the self.HomingX and self.HomingY are not reinitialzed here
            # The rationale is that the offset for the previous registration point is
            # probably a good starting point for this registration point..
            if (self.inMeasureOnlyMode):
                self.HomingX = 0.0
                self.HomingY = 0.0
            self.HomingPosX += self.HomingScanDirection
            if ((self.HomingPosX==maxX+1) or (self.HomingPosX==minX-1)):
                if self.HomingPosX == maxX+1:
                    self.HomingPosX = maxX
                else:
                    self.HomingPosX = minX
                self.HomingScanDirection *= -1
                self.HomingPosY -= 1
        if (self.HomingPosY!=maxY-1):
            self.HomeIn()
        else:
            self.inAutoMode = False
            print "Calibration Completed"
            self.printCalibrationErrorValue()




    def on_HomeToPos(self, posX, posY):
        self.HomingPosX = posX
        self.HomingPosY = posY
        self.HomeIn()

    def HomeIn(self):
        _posX = round(self.HomingPosX*3.0+self.HomingX/25.4,4)
        _posY = round(self.HomingPosY*3.0+self.HomingY/25.4,4)
        print "Moving to:[{}, {}]".format(_posX, _posY)
        self.data.units = "INCHES"
        self.data.gcode_queue.put("G20 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X"+str(_posX)+" Y"+str(_posY)+"  ")
        self.data.gcode_queue.put("G91  ")
        self.data.measureRequest = self.on_CenterOnSquare
        #request a measurement
        self.data.gcode_queue.put("B10 L")

    def on_CenterOnSquare(self, doCalibrate=False, findCenter=False):
        print "Analyzing Images"
        dxList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        dyList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        diList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        xBList = np.zeros(shape=(10))
        yBList = np.zeros(shape=(10))
        print "here"
        x = 0
        while True:
        #for x in range(10):  #review 10 images
            #print x
            ret, image = self.ids.KivyCamera.getCapture()
            if ret:
                self.ids.MeasuredImage.update(image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (5, 5), 0)
                edged = cv2.Canny(gray, 50, 100)
                edged = cv2.dilate(edged, None, iterations=1)
                edged = cv2.erode(edged, None, iterations=1)
                cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                (cnts, _) = contours.sort_contours(cnts)
                colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0), (255, 0, 255))
                refObj = None
                height, width, channels = image.shape

                if self.opticalCenter[0] is None or self.opticalCenter[1] is None:
                    xA = int(width/2)
                    yA = int(height/2)
                else:
                    xA, yA = self.opticalCenter

                # Draw a center marker on the video (for spot-checking that we hit the target)
                self.ids.KivyCamera.canvas.remove_group('center_marker')
                print "Using optical center (%.2f, %.2f)" % (xA, yA)
                self.drawCrosshairOnVideoForImagePoint(xA, yA, width, height, colors[4], group='center_marker')

                orig = image.copy()
                maxArea = 0
                for cTest in cnts:
                    if (cv2.contourArea(cTest)>maxArea):
                        maxArea = cv2.contourArea(cTest)
                        c = cTest
                if cv2.contourArea(c)>1000:
                    #approximate to a square (i.e., four contour segments)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                    #simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
                    if (findCenter):
                        sides = 20
                    else:
                        sides = 4
                    c=self.simplifyContour(c,sides)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                    box = cv2.minAreaRect(c)
                    angle = box[-1]
                    if (abs(angle+90)<30):
                        _angle = angle+90
                    else:
                        _angle = angle

                    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                    box = np.array(box, dtype="int")
                    box = perspective.order_points(box)

                    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
                    if findCenter == False:
                        M = cv2.getRotationMatrix2D((xA,yA),_angle,1)
                        orig = cv2.warpAffine(orig,M,(width,height))

                    xB = np.average(box[:, 0])
                    yB = np.average(box[:, 1])

                    if doCalibrate == True:
                        (tl, tr, br, bl) = box
                        (tlblX, tlblY) = self.midpoint(tl, bl)
                        (trbrX, trbrY) = self.midpoint(tr, br)
                        (tltrX, tltrY) = self.midpoint(tl, tr)
                        (blbrX, blbrY) = self.midpoint(bl, br)

                        self.xD = dist.euclidean((tlblX,tlblY),(trbrX,trbrY))/self.markerX
                        self.yD = dist.euclidean((tltrX,tltrY),(blbrX,blbrY))/self.markerY
                        self.ids.OpticalCalibrationAutoMeasureButton.disabled = False


                    cos = math.cos(angle*3.141592/180.0)
                    sin = math.sin(angle*3.141592/180.0)
                    if (_angle<30):
                        _angle = _angle *-1.0
                    #print _angle
                    if findCenter == False:
                        xB,yB = self.translatePoint(xB,yB,xA,yA,_angle)

                    #cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
                    self.drawCrosshairOnImage(orig, xA, yA, colors[0])
                    self.drawCrosshairOnImage(orig, xB, yB, colors[3])

                    #Dist = dist.euclidean((xA, yA), (xB, yB)) / self.D
                    Dx = dist.euclidean((xA,0), (xB,0))/self.xD
                    if (xA>xB):
                        Dx *= -1
                    Dy = dist.euclidean((0,yA), (0,yB))/self.yD
                    if (yA<yB):
                        Dy *= -1
                    Dist = math.sqrt(Dx**2.0 + Dy**2.0 )
                    dxList[x] = Dx
                    dyList[x] = Dy
                    diList[x] = Dist
                    xBList[x] = xB
                    yBList[x] = yB
                    x +=1
                    print "Processed Image #"+str(x)
                    if (x==10):
                        break
        print "Done Analyzing Images.. Now Averaging and Removing Outliers"
        if dxList.ndim != 0 :
            avgDx, stdDx = self.removeOutliersAndAverage(dxList)
            avgDy, stdDy = self.removeOutliersAndAverage(dyList)
            avgDi, stdDi = self.removeOutliersAndAverage(diList)
            avgxB, stdxB = self.removeOutliersAndAverage(xBList)
            avgyB, stdyB = self.removeOutliersAndAverage(yBList)
            if ( math.isnan(avgDx) or math.isnan(avgDy) ):
                print "Value is not a number: "+str(avgDx)+", "+str(avgDy)
                print "Aborting process."
            else:
                cv2.putText(orig, "("+str(self.HomingPosX)+", "+str(self.HomingPosY)+")",(15, 15),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                cv2.putText(orig, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(Dx,Dy,Dist), (15, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                cv2.putText(orig, "({:.3f}, {:.3f})".format(avgxB,avgyB), (15, 65),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                self.ids.MeasuredImage.update(orig)
                self.HomingX += avgDx#-self.calX
                self.HomingY += avgDy#-self.calY
                print "testing location"
                if doCalibrate!=True:  #its either True because you pressed the calibrate button or its a distance from the measurement callback.
                    if (((abs(avgDx)>=0.125) or (abs(avgDy)>=0.125)) and (self.inMeasureOnlyMode==False) and (findCenter==False)):
                        print "Adjusting Location"
                        self.HomeIn()
                    else:
                        print "Averagedx="+str(avgDx)+", Averagedy="+str(avgDy)
                        print str(self.HomingPosX+15)+", "+str(7-self.HomingPosY)+", "+str(self.HomingX)
                        if (self.inMeasureOnlyMode):
                            self.measuredErrorsX[self.HomingPosX+15][7-self.HomingPosY] = self.HomingX
                            self.measuredErrorsY[self.HomingPosX+15][7-self.HomingPosY] = self.HomingY
                        elif (findCenter==False):
                            self.calErrorsX[self.HomingPosX+15][7-self.HomingPosY] = self.HomingX
                            self.calErrorsY[self.HomingPosX+15][7-self.HomingPosY] = self.HomingY
                        else:
                            self.ids.centerX.text = "%.1f" % avgxB
                            self.ids.centerY.text = "%.1f" % avgyB
                            self.opticalCenter = (avgxB, avgyB)
                        self.updateScreenValues(self.HomingPosX, self.HomingPosY)
                        if (self.inAutoMode):
                            self.on_AutoHome()
                        else:
                            print "Done"
                else:
                    self.updateScreenValues()
        else:
            popup=Popup(title="Error", content = Label(text="Could not find square"), size_hint=(None,None), size=(400,400))
            popup.open()

    def drawCrosshairOnImage(self, image, x, y, color, thickness=1):
        cv2.circle(image, (int(x), int(y)), 10, color, thickness)
        cv2.line(image, (int(x), int(y) - 15), (int(x), int(y) + 15), color, thickness)
        cv2.line(image, (int(x) - 15, int(y)), (int(x) + 15, int(y)), color, thickness)

    def imagePointToWidgetPoint(self, ix, iy, iwidth, iheight, widget):
        wsize = widget.size
        videoSize = (wsize[0], wsize[0] * (float(iheight) / float(iwidth)))
        videoOffsetY = (wsize[1] - videoSize[1]) / 2
        wx = (float(ix) / iwidth) * videoSize[0]
        wy = wsize[1] - ((float(iy) / iheight) * videoSize[1] + videoOffsetY)
        return wx, wy

    def drawCrosshairOnVideoForImagePoint(self, ix, iy, iwidth, iheight, color=(1., 0, 0), group='overlay'):
        widget = self.ids.KivyCamera
        with widget.canvas:
            Color(*color)
            wx, wy = self.imagePointToWidgetPoint(ix, iy, iwidth, iheight, widget)
            Line(circle=(widget.x+wx, widget.y+wy, 2), group=group)

    def drawCircleOnVideo(self, cx, cy, r, iwidth, iheight, color=(1., 0, 0)):
        widget = self.ids.KivyCamera
        with widget.canvas:
            Color(*color)
            wx, wy = self.imagePointToWidgetPoint(cx, cy, iwidth, iheight, widget)
            wr = (r / iwidth) * widget.size[0]
            Line(circle=(widget.x+wx, widget.y+wy, wr), group='overlay')

    def on_centerReset(self):
        self.cameraCenteringPoints = []
        self.ids.KivyCamera.canvas.remove_group('overlay')

    def on_updateCenterX(self, value=(0,False)):
        if value[1] is False:
            try:
                cX = float(self.ids.centerX.text)
                self.opticalCenter = (cX, self.opticalCenter[1])
            except TypeError:
                print "Value not float"
                self.ids.centerX.text = ""

    def on_updateCenterY(self, value=(0,False)):
        if value[1] is False:
            try:
                cY = float(self.ids.centerY.text)
                self.opticalCenter = (self.opticalCenter[0], cY)
            except TypeError:
                print "Value not float"
                self.ids.centerY.text = ""

    def on_centerCalibrate(self):
        ret, image = self.ids.KivyCamera.getCapture()
        if ret is False:
            Popup(title="Error", content=Label(text="Could not capture image"),
                  size_hint=(None, None), size=(400, 400)).open()

        self.ids.MeasuredImage.update(image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(gray, 50, 100)
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
        (cnts, _) = contours.sort_contours(cnts)
        height, width, channels = image.shape

        colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0),
                  (255, 0, 255))

        orig = image.copy()
        maxArea = 0
        c = 0
        for cTest in cnts:
            if cv2.contourArea(cTest) > maxArea:
                maxArea = cv2.contourArea(cTest)
                c = cTest

        if cv2.contourArea(c) <= 1000:
            Popup(title="Error", content=Label(text="cv2.contourArea(c) <= 1000 (bad I think?)"),
                  size_hint=(None, None), size=(400, 400)).open()
            return

        # approximate to a square (i.e., four contour segments)
        cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
        # simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
        c = self.simplifyContour(c)
        cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
        box = cv2.minAreaRect(c)

        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(
            box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)

        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

        xB = np.average(box[:, 0])
        yB = np.average(box[:, 1])

        self.drawCrosshairOnImage(orig, xB, yB, colors[3])
        self.ids.MeasuredImage.update(orig)
        self.drawCrosshairOnVideoForImagePoint(xB, yB, width, height)

        self.cameraCenteringPoints.append((xB, yB))
        if len(self.cameraCenteringPoints) >= 3:
            # TODO: Average over all (or at least some) possible circles for the center point and radius
            # TODO: Sanity check that the circle is sane
            cX, cY = calculateCenterOfArc(self.cameraCenteringPoints[-3], self.cameraCenteringPoints[-2], self.cameraCenteringPoints[-1])
            self.ids.KivyCamera.canvas.remove_group('center_marker')
            self.drawCrosshairOnVideoForImagePoint(cX, cY, width, height, colors[4], group='center_marker')
            print "found a potential center point: %f, %f" % (cX, cY)
            radius = dist.euclidean((cX, cY),(self.cameraCenteringPoints[-1][0], self.cameraCenteringPoints[-1][1]))
            self.drawCircleOnVideo(cX, cY, radius, width, height)
            self.ids.centerX.text = "%.1f" % cX
            self.ids.centerY.text = "%.1f" % cY
            self.opticalCenter = (cX, cY)

    def on_surfaceFit(self):
        # set data into proper format
        dataX = np.zeros(((15*31),3))
        dataY = np.zeros(((15*31),3))
        for y in range(7, -8, -1):
            for x in range(-15, 16, +1):
                dataX[(7-y)*31+(x+15)][0]=float(x*3.0*25.4)
                dataY[(7-y)*31+(x+15)][0]=float(x*3.0*25.4)
                dataX[(7-y)*31+(x+15)][1]=float(y*3.0*25.4)
                dataY[(7-y)*31+(x+15)][1]=float(y*3.0*25.4)
                dataX[(7-y)*31+(x+15)][2]=self.calErrorsX[x+15][7-y]
                dataY[(7-y)*31+(x+15)][2]=self.calErrorsY[x+15][7-y]
        #surface fit X Errors
        xA = np.c_[np.ones(dataX.shape[0]), dataX[:,:2], np.prod(dataX[:,:2], axis=1), dataX[:,:2]**2]
        self.xCurve,_,_,_ = np.linalg.lstsq(xA, dataX[:,2],rcond=None)
        xB = dataX[:,2]
        xSStot = ((xB-xB.mean())**2).sum()
        xSSres = ((xB-np.dot(xA,self.xCurve))**2).sum()
        if (xSStot!=0):
            xR2 = 1.0 - xSSres / xSStot
        else:
            xR2 = 0.0
        #surface fit Y Errors
        yA = np.c_[np.ones(dataY.shape[0]), dataY[:,:2], np.prod(dataY[:,:2], axis=1), dataY[:,:2]**2]
        self.yCurve,_,_,_ = np.linalg.lstsq(yA, dataY[:,2],rcond=None)
        yB = dataY[:,2]
        ySStot = ((yB-yB.mean())**2).sum()
        ySSres = ((yB-np.dot(yA,self.yCurve))**2).sum()
        if (ySStot!=0):
            yR2 = 1.0 - ySSres / ySStot
        else:
            yR2 = 0.0

        #update screen
        line = "X Coefficients: "
        count=0
        for c in self.xCurve:
            line+= str(float(round(c,2)))
            if count!=5:
                line += ", "
                count += 1
        self.ids.xCoefficients.text = line + " ("+str(float(round(xR2,2)))+")"

        line = "Y Coefficients: "
        count=0
        for c in self.yCurve:
            line+= str(float(round(c,2)))
            if count!=5:
                line += ", "
                count += 1
        self.ids.yCoefficients.text = line + " ("+str(float(round(yR2,2)))+")"

        self.drawCalibration()
