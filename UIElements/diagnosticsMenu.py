from kivy.uix.floatlayout                        import    FloatLayout
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from   UIElements.scrollableTextPopup            import   ScrollableTextPopup
from   kivy.uix.popup                            import   Popup

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
    
    def testMotors(self):
        self.data.gcode_queue.put("B04 ")
        self.parentWidget.close()
    
