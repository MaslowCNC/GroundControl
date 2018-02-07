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

        #Convert to JSON data so caller can get tuples back
        self.backgroundTLHSV = json.dumps(self.data.backgroundTLHSV)
        self.backgroundTRHSV = json.dumps(self.data.backgroundTRHSV)
        self.backgroundBLHSV = json.dumps(self.data.backgroundBLHSV)
        self.backgroundBRHSV = json.dumps(self.data.backgroundBRHSV)
        self.backgroundTRPOS = json.dumps(self.data.backgroundTRPOS)
        self.backgroundTLPOS = json.dumps(self.data.backgroundTLPOS)
        self.backgroundBLPOS = json.dumps(self.data.backgroundBLPOS)
        self.backgroundBRPOS = json.dumps(self.data.backgroundBRPOS)
        
    def closeit(self):
        #ToDo: Not sure why I have to copy all this back, but I do:
        self.backgroundTLHSV = self.tlhsv.text
        self.backgroundTRHSV = self.trhsv.text
        self.backgroundBLHSV = self.blhsv.text
        self.backgroundBRHSV = self.brhsv.text
        self.backgroundTRPOS = self.trpos.text
        self.backgroundTLPOS = self.tlpos.text
        self.backgroundBLPOS = self.blpos.text
        self.backgroundBRPOS = self.brpos.text
        
        self.close(self) #Call the callback
        
