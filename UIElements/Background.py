from kivy.uix.screenmanager                 import Screen
from kivy.properties                        import ObjectProperty
from DataStructures.makesmithInitFuncs      import MakesmithInitFuncs


class Background(Screen, MakesmithInitFuncs):
    backgroundmenu  = ObjectProperty(None) #make BackgroundMenu object accessible at this scope
    close       = ObjectProperty(None)
    
    def setUpData(self, data):
        self.data = data
        #self.backgroundmenu.setUpData(data)
        #self.backgroundmenu.parentWidget = self
