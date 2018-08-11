from kivy.uix.gridlayout                       import   GridLayout
from kivy.properties                           import   StringProperty
from DataStructures.makesmithInitFuncs         import MakesmithInitFuncs
import ast


class BackgroundSettingsDlg(GridLayout, MakesmithInitFuncs):
    # Set my variables to proper type that TextInput expects
    backgroundTRPOS = StringProperty('')
    backgroundTLPOS = StringProperty('')
    backgroundBLPOS = StringProperty('')
    backgroundBRPOS = StringProperty('')
    backgroundTLManualReg = StringProperty('')
    backgroundTRManualReg = StringProperty('')
    backgroundBLManualReg = StringProperty('')
    backgroundBRManualReg = StringProperty('')

    def __init__(self, data, **kwargs):
        super(BackgroundSettingsDlg, self).__init__(**kwargs)
        self.data = data
        # Set local variables
        self.backgroundTLPOS = str(self.data.backgroundAlignment[0])
        self.backgroundTRPOS = str(self.data.backgroundAlignment[1])
        self.backgroundBLPOS = str(self.data.backgroundAlignment[2])
        self.backgroundBRPOS = str(self.data.backgroundAlignment[3])
        self.backgroundTLManualReg = str(self.data.backgroundManualReg[0])
        self.backgroundTLManualReg = str(self.data.backgroundManualReg[0])
        self.backgroundTRManualReg = str(self.data.backgroundManualReg[1])
        self.backgroundBLManualReg = str(self.data.backgroundManualReg[2])
        self.backgroundBRManualReg = str(self.data.backgroundManualReg[3])

    def closeit(self):
        # If data is malformed dont update the variables
        try:
            self.data.backgroundManualReg[0] =\
                ast.literal_eval(self.ids.tlmanualreg.text)
            self.data.backgroundManualReg[1] =\
                ast.literal_eval(self.ids.trmanualreg.text)
            self.data.backgroundManualReg[2] =\
                ast.literal_eval(self.ids.blmanualreg.text)
            self.data.backgroundManualReg[3] =\
                ast.literal_eval(self.ids.brmanualreg.text)
            self.data.backgroundAlignment[0] =\
                ast.literal_eval(self.ids.tlpos.text)
            self.data.backgroundAlignment[1] =\
                ast.literal_eval(self.ids.trpos.text)
            self.data.backgroundAlignment[2] =\
                ast.literal_eval(self.ids.blpos.text)
            self.data.backgroundAlignment[3] =\
                ast.literal_eval(self.ids.brpos.text)
        except Exception as e:
            print(e)
        self.close(self)
