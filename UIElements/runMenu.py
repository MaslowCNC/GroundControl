from kivy.uix.floatlayout import FloatLayout

class RunMenu(FloatLayout):
    
    def closeGC(self):
        '''
        
        Exit the program.
        
        '''
        from kivy.app import App
        App.get_running_app().stop()
    
    def returnToCenter(self):
        self.data.gcode_queue.put("G00 Z0 ")
        self.data.gcode_queue.put("G00 X0 Y0 Z0 ")
        self.parentWidget.close()