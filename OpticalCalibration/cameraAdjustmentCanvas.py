from kivy.uix.gridlayout                     import GridLayout
from kivy.properties                         import NumericProperty, ObjectProperty, BooleanProperty
from kivy.graphics                           import Color, Ellipse, Line, InstructionGroup
from kivy.graphics.texture                   import Texture
from kivy.graphics.transformation            import Matrix
from kivy.core.window                        import Window
from kivy.graphics.transformation            import Matrix
from kivy.clock                              import Clock
from kivy.uix.image                          import Image
from kivy.app                                import App
from kivy.uix.popup                          import Popup
from kivy.uix.label                          import Label
from UIElements.positionIndicator            import PositionIndicator
from OpticalCalibration.cameraCenterCalibration import calculateCenterOfArc
from OpticalCalibration.opticalCalibrationCanvas   import KivyCamera
from OpticalCalibration.opticalCalibrationCanvas        import MeasuredImage
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

class CameraAdjustmentCanvas(GridLayout):

    capture = None
    cameraCount = 0
    xD = 1
    yD = 1
    done = ObjectProperty(None)
    currentX, currentY = 0, 0
    calX = 0
    calY = 0

    markerX = 0.5*25.4
    markerY = 0.5*25.4
    counter =0
    bedHeight = 48*25.4
    bedWidth = 96*25.4

    gaussianBlurValue = 0
    cannyLowValue = 0
    cannyHighValue = 0

    #def initialize(self):

    def initialize(self):
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
        self.gaussianBlurValue = int(self.data.config.get('Optical Calibration Settings', 'gaussianBlurValue'))
        self.cannyLowValue = float(self.data.config.get('Optical Calibration Settings', 'cannyLowValue'))
        self.cannyHighValue = float(self.data.config.get('Optical Calibration Settings', 'cannyHighValue'))
        self.ids.gaussianBlur.value = self.gaussianBlurValue
        self.ids.cannyLow.value = self.cannyLowValue
        self.ids.cannyHigh.value = self.cannyHighValue

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

    def midpoint(self, ptA, ptB):
        return ((ptA[0]+ptB[0])*0.5, (ptA[1]+ptB[1])*0.5)

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

    def do_Exit(self):
        if self.capture != None:
            self.capture.release()
            self.capture = None
            self.parent.parent.parent.dismiss()

    def on_SaveSettings(self):
        App.get_running_app().data.config.set('Optical Calibration Settings', 'gaussianBlurValue', self.gaussianBlurValue)
        App.get_running_app().data.config.set('Optical Calibration Settings', 'cannyLowValue', self.cannyLowValue)
        App.get_running_app().data.config.set('Optical Calibration Settings', 'cannyHighValue', self.cannyHighValue)

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

    def onGaussianBlur(self):
        self.gaussianBlurValue = int(self.ids.gaussianBlur.value)
        self.ids.gaussianBlurValueLabel.text = "("+str(self.gaussianBlurValue)+")"
        self.on_updateCapturedImage()

    def onCannyLow(self):
        self.cannyLowValue = float(self.ids.cannyLow.value)
        self.ids.cannyLowValueLabel.text = "("+str(self.cannyLowValue)+")"
        self.on_updateCapturedImage()

    def onCannyHigh(self):
        self.cannyHighValue = float(self.ids.cannyHigh.value)
        self.ids.cannyHighValueLabel.text = "("+str(self.cannyHighValue)+")"
        self.on_updateCapturedImage()


    def on_touch_up(self, touch):

        if touch.is_mouse_scrolling:
            self.zoomCanvas(touch)


    def removeOutliersAndAverage(self, data):
        mean = np.mean(data)
        #print "mean:"+str(mean)
        sd = np.std(data)
        #print "sd:"+str(sd)
        tArray = [x for x in data if ( (x >= mean-2.0*sd) and (x<=mean+2.0*sd))]
        return np.average(tArray), np.std(tArray)

    def on_ReturnToCenter(self):
        print "Moving to:[0, 0]"
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X0 Y0  ")
        self.data.gcode_queue.put("G91  ")


    def HomeIn(self):
        _posX = round(self.HomingPosX*3.0+self.HomingX/25.4,4)
        _posY = round(self.HomingPosY*3.0+self.HomingY/25.4,4)
        self.updateTargetIndicator(_posX,_posY,"INCHES")
        print "Moving to ({},{}) by trying [{}, {}]".format(self.HomingPosX*3.0, self.HomingPosY*3.0,_posX, _posY)
        self.data.units = "INCHES"
        self.data.gcode_queue.put("G20 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X"+str(_posX)+" Y"+str(_posY)+"  ")
        self.data.gcode_queue.put("G91  ")
        self.data.measureRequest = self.on_CenterOnSquare
        #request a measurement
        self.data.gcode_queue.put("B10 L")

    def on_updateCapturedImage(self, valueChange = 0):
        print "Analyzing Images"
        dxList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        dyList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        diList = np.zeros(shape=(10))#[-9999.9 for x in range(10)]
        xBList = np.zeros(shape=(10))
        yBList = np.zeros(shape=(10))
        x = 0
        falseCounter = 0
        while True:
        #for x in range(10):  #review 10 images
            #print x
            ret, image = self.ids.KivyCamera.getCapture()
            if ret:
                #self.ids.MeasuredImage.update(image)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (self.gaussianBlurValue, self.gaussianBlurValue), 0)
                coloredGray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                self.ids.GrayedImage.update(coloredGray)
                edged = cv2.Canny(gray, self.cannyLowValue, self.cannyHighValue)
                edged = cv2.dilate(edged, None, iterations=1)
                edged = cv2.erode(edged, None, iterations=1)
                coloredEdged = cv2.cvtColor(edged, cv2.COLOR_GRAY2BGR)
                self.ids.EdgedImage.update(coloredEdged)
                #self.ids.EdgedImage.update(edged)
                cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]
                (cnts, _) = contours.sort_contours(cnts)
                colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0), (255, 0, 255))
                refObj = None
                height, width, channels = image.shape
                xA = width / 2.0
                yA = height / 2.0
                maxArea = 0
                for cTest in cnts:
                    if (cv2.contourArea(cTest)>maxArea):
                        maxArea = cv2.contourArea(cTest)
                        c = cTest
                if cv2.contourArea(c)>1000:
                    orig = image.copy()
                    #approximate to a square (i.e., four contour segments)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                    #simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
                    sides = 4
                    c=self.simplifyContour(c,sides)
                    cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                    box = cv2.minAreaRect(c)

                    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                    box = np.array(box, dtype="int")
                    box = perspective.order_points(box)

                    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

                    xB = np.average(box[:, 0])
                    yB = np.average(box[:, 1])

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
                    self.ids.MeasuredImage.update(orig)
                    #print "Processed Image #"+str(x)
                    if (x==10):
                        break
                else:
                    falseCounter += 1
                    if (falseCounter == 10):
                        break
            else:
                falseCounter += 1
                if (falseCounter == 10):
                    break

        print "Got images, "+str(falseCounter)+" images were bad"
        print "Done Analyzing Images.. Now Averaging and Removing Outliers"
        if dxList.ndim != 0 and falseCounter!=10:
            avgDx, stdDx = self.removeOutliersAndAverage(dxList)
            avgDy, stdDy = self.removeOutliersAndAverage(dyList)
            avgDi, stdDi = self.removeOutliersAndAverage(diList)
            avgxB, stdxB = self.removeOutliersAndAverage(xBList)
            avgyB, stdyB = self.removeOutliersAndAverage(yBList)
            if ( math.isnan(avgDx) or math.isnan(avgDy) ):
                print "Value is not a number: "+str(avgDx)+", "+str(avgDy)
                print "Aborting process."
            else:
                cv2.putText(orig, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(Dx,Dy,Dist), (15, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                cv2.putText(orig, "({:.3f}, {:.3f})".format(avgxB,avgyB), (15, 65),cv2.FONT_HERSHEY_SIMPLEX, 0.55, colors[0], 2)
                self.ids.MeasuredImage.update(orig)

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
