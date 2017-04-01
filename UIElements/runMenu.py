from kivy.uix.floatlayout import FloatLayout

class RunMenu(FloatLayout):
    
    def closeGC(self):
        '''
        
        Exit the program.
        
        '''
        from kivy.app import App
        App.get_running_app().stop()

