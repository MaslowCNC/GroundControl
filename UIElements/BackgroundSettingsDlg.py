from   kivy.uix.gridlayout                       import   GridLayout
from   kivy.properties                           import   ObjectProperty
from   kivy.properties                           import   StringProperty
from DataStructures.makesmithInitFuncs           import MakesmithInitFuncs
from   kivy.clock                                import Clock
import json

class BackgroundSettingsDlg(GridLayout, MakesmithInitFuncs):
    backgroundTLHSV = StringProperty("[(30,40,80),(90,255,255)]")
    backgroundTRHSV = StringProperty("[(160, 60, 40),(10,255,255)]")
    backgroundBLHSV = StringProperty("[(90,60,80),(140,255,255)]")
    backgroundBRHSV = StringProperty("[(160, 60, 40),(10,255,255)]")
    backgroundTRPOS = StringProperty("( 1225, 615)")
    backgroundTLPOS = StringProperty("(-1225, 615)")
    backgroundBLPOS = StringProperty("(-1225,-615)")
    backgroundBRPOS = StringProperty("( 1225,-615)")

    def __init__(self, data, **kwargs):
        super(BackgroundSettingsDlg, self).__init__(**kwargs)
        self.data = data
        print "Dumped '"+json.dumps(self.data.backgroundTLHSV)+"'"
        backgroundTLHSV = json.dumps(self.data.backgroundTLHSV)
        backgroundTRHSV = json.dumps(self.data.backgroundTRHSV)
        backgroundBLHSV = json.dumps(self.data.backgroundBLHSV)
        backgroundBRHSV = json.dumps(self.data.backgroundBRHSV)
        backgroundTRPOS = json.dumps(self.data.backgroundTRPOS)
        backgroundTLPOS = json.dumps(self.data.backgroundTLPOS)
        backgroundBLPOS = json.dumps(self.data.backgroundBLPOS)
        backgroundBRPOS = json.dumps(self.data.backgroundBRPOS)
        Clock.schedule_once(self.open)
        
    def open(self, *args):
        print "ODumped '"+json.dumps(self.data.backgroundTLHSV)+"'"
        backgroundTLHSV = json.dumps(self.data.backgroundTLHSV)
        backgroundTRHSV = json.dumps(self.data.backgroundTRHSV)
        backgroundBLHSV = json.dumps(self.data.backgroundBLHSV)
        backgroundBRHSV = json.dumps(self.data.backgroundBRHSV)
        backgroundTRPOS = json.dumps(self.data.backgroundTRPOS)
        backgroundTLPOS = json.dumps(self.data.backgroundTLPOS)
        backgroundBLPOS = json.dumps(self.data.backgroundBLPOS)
        backgroundBRPOS = json.dumps(self.data.backgroundBRPOS)

        
    def closeit(self):
        self.close(self)
