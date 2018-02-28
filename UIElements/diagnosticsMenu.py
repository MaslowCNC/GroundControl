from kivy.uix.floatlayout                        import    FloatLayout
from DataStructures.makesmithInitFuncs           import    MakesmithInitFuncs
from UIElements.scrollableTextPopup              import    ScrollableTextPopup
from kivy.uix.popup                              import    Popup
from CalibrationWidgets.calibrationFrameWidget   import    CalibrationFrameWidget
from CalibrationWidgets.calibrateLengthsPopup    import    CalibrateLengthsPopup
from Simulation.simulationCanvas                 import    SimulationCanvas
from kivy.clock                                  import    Clock
import sys

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
        if sys.platform.startswith('darwin'):
            self._popup = Popup(title="About GroundControl", content=content, size=(520,400), size_hint=(.6, .6))
        else:
            self._popup = Popup(title="About GroundControl", content=content, size=(520,400), size_hint=(None, None))
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
        
        self.popupContent.establishDataConnection(self.data)
        
        self._popup = Popup(title="Calibrate Chain Lengths", content=self.popupContent,
                            size_hint=(0.85, 0.95), auto_dismiss = False)
        self._popup.open()
    
    def manualCalibrateChainLengths(self):
        self.data.gcode_queue.put("B08 ")
        self.parentWidget.close()
    
    def testMotors(self):
        self.data.gcode_queue.put("B04 ")
        self.parentWidget.close()
    
    def wipeEEPROM(self):
        self.data.gcode_queue.put("$RST=* ")
        Clock.schedule_once(self.data.pushSettings, 6)
        self.parentWidget.close()
    
    def calibrateMachine(self):
        '''
        
        Spawns a walk through that helps the user measure the machine's dimensions
        
        '''
        self.popupContent       = CalibrationFrameWidget(done=self.dismissCalibrationPopup)
        self.popupContent.on_Enter()
        self._popup = Popup(title="Calibration", content=self.popupContent,
                            size_hint=(0.95, 0.95), auto_dismiss = False)
        self._popup.open()
    
    def dismissCalibrationPopup(self):
        '''
        
        Close The calibration Pop-up
        
        '''
        self.data.calibrationInProcess = False
        self._popup.dismiss()
    
    def launchSimulation(self):
        print "launch simulation"
        self.popupContent      = SimulationCanvas()
        self.popupContent.data = self.data
        self.popupContent.initialize()
        self._popup = Popup(title="Maslow Calibration Simulation", content=self.popupContent,
                            size_hint=(0.85, 0.95), auto_dismiss = True)
        self._popup.open()
        self.parentWidget.close()
    
    def loadCalibrationBenchmarkTest(self):
        '''
        
        Loads the Calibration Benchmark Test file
        
        '''
        self.data.gcodeFile = "./gcodeForTesting/Calibration Benchmark Test.nc"
        self.parentWidget.close()
    
    def advancedOptionsFunctions(self, text):
        
        if   text == "Test Feedback System":
            self.testFeedbackSystem()
        elif text == "Set Chain Length - Manual":
            self.manualCalibrateChainLengths()
        elif text == "Wipe EEPROM":
            self.wipeEEPROM()
        elif text == "Simulation":
            self.launchSimulation()
        elif text == "Load Calibration Benchmark Test":
            self.loadCalibrationBenchmarkTest()
