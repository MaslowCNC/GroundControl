from kivy.uix.screenmanager                 import Screen
from kivy.properties                        import ObjectProperty
from DataStructures.makesmithInitFuncs      import MakesmithInitFuncs


class OtherFeatures(Screen, MakesmithInitFuncs):
    viewmenu = ObjectProperty(None) #make viewmenu object accessible at this scope
    
    def setUpData(self, data):
        self.data = data
        print "Initialized: " + str(self) 
        self.viewmenu.setUpData(data)