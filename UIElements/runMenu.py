from kivy.uix.floatlayout import FloatLayout

class RunMenu(FloatLayout):
    
    def closeGC(self):
        '''
        
        Exit the program.
        
        '''
        from kivy.app import App
        App.get_running_app().stop()
    
    def returnToCenter(self):
        
        self.data.gcode_queue.put("G90  ")
        
        safeHeightMM = float(self.data.config.get('Maslow Settings', 'zAxisSafeHeight'))
        safeHeightInches = safeHeightMM / 25.5
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
        else:
            self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
        
        self.data.gcode_queue.put("G00 X0.0 Y0.0 ")
            
        #close the actions popup
        self.parentWidget.close()
            