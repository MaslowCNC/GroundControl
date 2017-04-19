from kivy.uix.floatlayout                        import    FloatLayout
from DataStructures.makesmithInitFuncs           import    MakesmithInitFuncs
from UIElements.scrollableTextPopup              import    ScrollableTextPopup
from kivy.uix.popup                              import    Popup
from UIElements.measureMachinePopup              import    MeasureMachinePopup

class Diagnostics(FloatLayout, MakesmithInitFuncs):
    
    def about(self):
        popupText = 'Ground Control v' + str(self.data.version) + ' allows you to control the Maslow machine. ' + \
                    'From within Ground Control, you can move the machine to where you want to begin a cut, calibrate the machine, ' + \
                    'open and run a g-code file, or monitor the progress of an ongoing cut. For more details see the Maslow website ' + \
                    'at http://www.maslowcnc.com/. The source code can be downloaded at https://github.com/MaslowCNC. ' + \
                    '\n\n' + \
                    'GroundControl is part of the of the Maslow Control Software Copyright (C) 2014-2017 Bar Smith. ' + \
                    'This program is free software: you can redistribute it and/or modify ' + \
                    'it under the terms of the GNU General Public License as published by ' + \
                    'the Free Software Foundation, either version 3 of the License, or ' + \
                    '(at your option) any later version. ' + \
                    '\n\n' + \
                    'This program is distributed in the hope that it will be useful, ' + \
                    'but WITHOUT ANY WARRANTY; without even the implied warranty of ' + \
                    'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the ' + \
                    'GNU General Public License for more details. ' + \
                    '\n\n' + \
                    'You should have received a copy of the GNU General Public License ' + \
                    'along with the Maslow Control Software. If not, see <http://www.gnu.org/licenses/>.'
                
        content = ScrollableTextPopup(cancel = self.dismiss_popup, text = popupText, markup = True)
        self._popup = Popup(title="About GroundControl", content=content, size_hint=(0.5, 0.5))
        self._popup.open()
    
    def dismiss_popup(self):
        '''
        
        Close The Pop-up
        
        '''
        self._popup.dismiss()
    
    def calibrateMotors(self):
        self.data.gcode_queue.put("B01")
        self.parentWidget.close()
        
    def calibrateChainLengths(self):
        self.data.gcode_queue.put("B02 ")
        self.parentWidget.close()
    
    def manualCalibrateChainLengths(self):
        self.data.gcode_queue.put("B06 L1900 R1900")
        self.data.message_queue.put("Message: The machine chains have been recalibrate to length 1,900mm")
        self.parentWidget.close()
    
    def testMotors(self):
        self.data.gcode_queue.put("B04 ")
        self.parentWidget.close()
    
    def testFeedbackSystem(self):
        print "Testing feedback system"
        self.data.gcode = ["G20 G90 G40","(profile 1)","T0 M6","G17","M3","G0 X-0.7989 Y-0.7218","G1 X0.3822 Y-0.7218 F25","G3 X0.3986 Y-0.7207 I0 J0.125","G1 X0.5514 Y-0.7006","G3 X0.5829 Y-0.6922 I-0.0163 J0.1239","G1 X0.7254 Y-0.6332","G3 X0.7536 Y-0.6169 I-0.0478 J0.1155","G1 X0.8759 Y-0.523","G3 X0.899 Y-0.4999 I-0.0761 J0.0992","G1 X0.9928 Y-0.3776","G3 X1.0092 Y-0.3494 I-0.0992 J0.0761","G1 X1.0682 Y-0.2069","G3 X1.0766 Y-0.1754 I-0.1155 J0.0478","G1 X1.0967 Y-0.0226","G3 X1.0978 Y-0.0063 I-0.1239 J0.0163","G3 X1.0967 Y0.0101 I-0.125 J0","G1 X1.0766 Y0.1629","G3 X1.0682 Y0.1944 I-0.1239 J-0.0163","G1 X1.0092 Y0.3369","G3 X0.9928 Y0.3651 I-0.1155 J-0.0478","G1 X0.899 Y0.4874","G3 X0.8759 Y0.5105 I-0.0992 J-0.0761","G1 X0.7536 Y0.6043","G3 X0.7254 Y0.6207 I-0.0761 J-0.0992","G1 X0.5829 Y0.6797","G3 X0.5514 Y0.6881 I-0.0478 J-0.1155","G1 X0.3986 Y0.7082","G3 X0.3822 Y0.7093 I-0.0163 J-0.1239","G1 X-0.7989 Y0.7093","G3 X-0.9239 Y0.5843 I0 J-0.125","G1 X-0.9239 Y-0.5968","G3 X-0.7989 Y-0.7218 I0.125 J0"]
        self.data.gcodeIndex = 0
        self.data.uploadFlag = True
        self.data.logger.beginRecordingAvgError()
        self.data.message_queue.put("Message: If you press \"Continue\" Maslow will run a small test shape and report the average positional error when finished. The z-axis will not move during this test.")
        self.parentWidget.close()
    
    def wipeEEPROM(self):
        self.data.gcode_queue.put("B07 ")
        self.parentWidget.close()
    
    def measureMachine(self):
        '''
        
        Spawns a walk through that helps the user measure the machine's dimensions
        
        '''
        self.popupContent      = MeasureMachinePopup(done=self.dismissMeasureMachinePopup)
        self.popupContent.data = self.data
        self._popup = Popup(title="Setup Machine Dimensions", content=self.popupContent,
                            size_hint=(0.8, 0.8))
        self._popup.open()
    
    def dismissMeasureMachinePopup(self):
        '''
        
        Close The measure machine Pop-up
        
        '''
        self._popup.dismiss()
    
    def advancedOptionsFunctions(self, text):
        
        if   text == "Test Feedback System":
            self.testFeedbackSystem()
        elif text == "Calibrate Chain Length - Manual":
            self.manualCalibrateChainLengths()
        elif text == "Wipe EEPROM":
            self.wipeEEPROM()