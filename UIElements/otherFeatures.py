from kivy.uix.screenmanager                           import Screen
from kivy.properties                                  import ObjectProperty
from DataStructures.makesmithInitializationFunctions  import MakesmithInitializationFunctions


class OtherFeatures(Screen, MakesmithInitializationFunctions):
    viewmenu = ObjectProperty(None) #make viewmenu object accessible at this scope
