from kivy.uix.floatlayout                        import    FloatLayout
from DataStructures.makesmithInitFuncs           import    MakesmithInitFuncs
from UIElements.scrollableTextPopup              import    ScrollableTextPopup
from kivy.uix.popup                              import    Popup
from UIElements.measureMachinePopup              import    MeasureMachinePopup
from UIElements.calibrateLengthsPopup            import    CalibrateLengthsPopup

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
        
    def calibrateChainLengths(self):
        #establish known initial conditions
        self.data.gcode_queue.put("B06 L0 R0 ");
        
        self.popupContent      = CalibrateLengthsPopup(done=self.dismissMeasureMachinePopup)
        self.popupContent.data = self.data
        self._popup = Popup(title="Calibrate Chain Lengths", content=self.popupContent,
                            size_hint=(0.85, 0.95))
        self._popup.open()
    
    def manualCalibrateChainLengths(self):
        self.data.gcode_queue.put("B08 ")
        self.parentWidget.close()
    
    def testMotors(self):
        self.data.gcode_queue.put("B04 ")
        self.parentWidget.close()
    
    def testFeedbackSystem(self):
        print "Testing feedback system"
        self.data.gcode = ["G20 ","G1 X-1 Y-1 F25 ", "G1 X1 ", "G3 Y2 J1.5", "G1 X-1 ", "G1 Y-1", "G1 X0 Y0"]
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
                            size_hint=(0.85, 0.95))
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