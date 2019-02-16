from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.bubble import Bubble
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty
from HoleyCalibration import HoleyCalibration


Builder.load_string("""
<ColoredLabel>:
  bcolor: 1, 1, 1, 1
  canvas.before:
    Color:
      rgba: self.bcolor
    Rectangle:
      pos: self.pos
      size: self.size
""")

class ColoredLabel(Label):
  bcolor = ListProperty([0,0,0,.5])

Factory.register('KivyB', module='ColoredLabel')
def get_id(root,instance):
    for id, widget in root.ids.items():
        if widget.__self__ == instance:
            return id
class hspc_MachineParameters(Widget):
    DictIds=['IsQuadKin','ChainOverSprocket','RotRad','SledWeight','MotorYOffset','DistBtwnMtrs','LftChTol','RghtChTol']
    def __init__(self):
        super(hspc_MachineParameters,self).__init__()
        self.Dict={}
        
    def Next(self):
        #Prepare machine parameters as input arguments
        #Launch next widget
        
        
        DictValues=[self.ids[k].text for k in self.DictIds]
        self.Dict=dict(zip(self.DictIds,DictValues))
        MeasWid=hspc_Measurements(self.Dict)
        self.clear_widgets()
        self.parent.add_widget(MeasWid)
        
    def Close(self):
        self.manager.current='hspc_Measurements'
        App.get_running_app().stop()
    def QuadKinPrintHello(self,value):
        #import pdb; pdb.set_trace()
        print("Hello.  QuadKin = "+value.text)
        self.ids['RotRad'].text=self.ids['IsQuadKin'].text
    pass

class hspc_Measurements(Widget):
    DictIds=['M{}'.format(num) for num in range(1,13)]
    def __init__(self,Dict):
        super(hspc_Measurements,self).__init__()
        self.Dict=Dict
        self.Cal=HoleyCalibration()
        self.Cal.InitializeIdealXyCoordinates()
    def Next(self):
        DictValues=[]
#        for k in self.DictIds:
#            val=self.ids[k].text
#            if val:
#                DictValues.append(float(val))
#            else:
#                DictValues.append(0.0)
        DictValues=[self.ids[k].text for k in self.DictIds]
        MeasDict=dict(zip(self.DictIds,DictValues))
        self.Dict.update(MeasDict)
        self.Dict.update({'CalObj':self.Cal})
        CalWid=hspc_Calibrate(self.Dict)
        self.clear_widgets()
        self.parent.add_widget(CalWid)
    def ValidateMeasurement(self,widget,focus):
        #import pdb; pdb.set_trace()
        if not focus and widget.text:
            Meas=float(widget.text)
            
            vid=get_id(self,widget)
            MeasNum=int(vid[1:])-1
            vl=vid+'Label'
            IsValid=self.Cal.ValidateMeasurement(Meas,MeasNum)
            
            if IsValid:
                self.ids[vl].bcolor=(0, 1, 0, 0.4) #green
            else:
                self.ids[vl].bcolor=(1, 0, 0, 0.4) #red
        
    #def __init__(self,MachineParams):
        #import pdb; pdb.set_trace()
        #self.cal=HoleyCalibration
        #pass
def LoadCalibrateWid():
    BaseStr= \
"""
<hspc_Calibrate>:
    BoxLayout:
        height: root.height
        width: root.width
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: .1
            ColoredLabel:
                size_hint_x: .1
                text: ""
                bcolor: 0,0,0,.5
            ColoredLabel:
                text: "Initial"
                bcolor: 0,0,0,.5
            ColoredLabel:
                text: "Calibrated"
                bcolor: 0,0,0,.5
        BoxLayout:
            orientation: 'vertical'
            GridLayout:
                cols: 5"""
    LabelFormat= \
"""
                Label:
                    size_hint_x: {0}
                    text: \"{1}\""""
    Labels=[(".3",""),("1","Measurement"),("1","Error"),("1","Length"),("1","Error")]
    Labels=''.join([LabelFormat.format(Width,Label) for Width,Label in Labels])
        
    Fmt=\
"""
                Label:
                    size_hint_x: .1
                    text: \"M{0}\"
                TextInput:
                    id: M{0}Meas
                TextInput:
                    id: M{0}MeasErr
                TextInput:
                    id: M{0}Cal
                TextInput:
                    id: M{0}CalErr"""
    mmts=['1','2','3','4','5','6','7','8','9','10','11','12']
    mmts=[Fmt.format(mmt) for mmt in mmts]
    mmts=''.join(mmts)
    CalBox=\
"""
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: .35
                Button:
                    size_hint_x: .5
                    text: 'Calibrate'
                    on_release: root.Calibrate()
                GridLayout:
                    cols: 3"""
    lblfmt=\
"""
                    Label:
                        text: \"{}\""""
    lbls=['','Initial','Calibrated']
    lbls=[lblfmt.format(lbl) for lbl in lbls]
    lblstr=''.join(lbls)
    inptfmt=\
"""
                    Label:
                        text: \"{0}\"
                    TextInput:
                        id: Init{0}
                    TextInput:
                        id: Cal{0}"""
    prms=['MotorYOffset','DistBtwnMtrs','LftChTol','RghtChTol']
    prms=''.join([inptfmt.format(prm) for prm in prms])
    ptm=\
"""
                Button:
                    size_hint_x: .5
                    text: 'Push to Machine'
                Button:
                    size_hint_x: .5
                    text: 'Quit'"""
    WidLayout=''.join([BaseStr,Labels,mmts,CalBox,lblstr,prms,ptm])
    Builder.load_string(WidLayout)
    #import pdb
    #pdb.set_trace()
    #return Wid
LoadCalibrateWid()
class hspc_Calibrate(Widget):
    def __init__(self,Dict):
        super(hspc_Calibrate,self).__init__()
        cal=Dict['CalObj']
        PrmIds=['MotorYOffset','DistBtwnMtrs','LftChTol','RghtChTol']
        InitIds=['Init{0}'.format(pid) for pid in PrmIds]
        CalIds=['Cal{0}'.format(cid) for cid in PrmIds]
        
        
        cal.InitializeIdealXyCoordinates()
        
        #Measurements and Measurement Error
        self.InitMeasIds=[('M{0}Meas'.format(meas),'M{0}'.format(meas),'M{0}MeasErr'.format(meas),meas) for meas in range(1,13)]
        MeasError=[]
        Measurements=[]
        for sid,did,side,idx in self.InitMeasIds:
            if Dict[did]:
                InitMeas=float(Dict[did])
            else:
                InitMeas=0.0
            Measurements.append(InitMeas)
            self.ids[sid].text=Dict[did]
            me=cal.InitialMeasurementError(InitMeas,idx-1)
            MeasError.append(me)
            self.ids[side].text=str(me)
        
        cal.SetMeasurements(Measurements)
        
        #Machine Parameters
        for iid,pid in zip(InitIds,PrmIds):
            self.ids[iid].text=Dict[pid]
        CalNames=\
            [('isQuadKinematics','IsQuadKin'),\
             ('SP_D','DistBtwnMtrs'),\
             ('SP_motorOffsetY','MotorYOffset'),\
             ('SP_rotationDiskRadius','RotRad'),\
             ('SP_leftChainTolerance','LftChTol'),\
             ('SP_rightChainTolerance','RghtChTol'),\
             ('SP_chainOverSprocket','ChainOverSprocket'),\
             ('SP_sledWeight','SledWeight')]
        for cn,dn in CalNames:
            if Dict[dn]:
                cal.__dict__[cn]=float(Dict[dn])
            else:
                cal.__dict__[cn]=0.0
        cal.kin.isQuadKinematics=bool(float(Dict['IsQuadKin']))
        cal.InitializeIdealXyCoordinates()
        self.Cal=cal
        
        
        
        
        self.Dict=Dict
    def Calibrate(self):
        
        self.Cal.Calibrate()
        self.CalibratedLengthsToGui()
        self.Cal.ReportCalibration()
        #self.CalibratedParamsToGui()
        #Push calibrated lengths to table
        #Push calibrated errors to table
        
    def CalibratedLengthsToGui(self):

        #
        #Push Calibrated Lengths and Erors to GUI
        CalLengths=self.Cal.CalibratedLengths()
        ce=self.Cal.CalibratedLengthError()
        
        for l,e,mid in zip(CalLengths,ce,range(1,len(CalLengths)+1)):
            self.ids['M{0}Cal'.format(mid)].text=str(l)
            self.ids['M{0}CalErr'.format(mid)].text=str(e)
        
        #Push Calibrated Parameters to GUI
        CalNames=\
            [('Opt_D','CalDistBtwnMtrs'),\
             ('Opt_motorOffsetY','CalMotorYOffset'),\
             ('Opt_leftChainTolerance','CalLftChTol'),\
             ('Opt_rightChainTolerance','CalRghtChTol')]
        for cn,gn in CalNames:
            self.ids[gn].text='{:4f}'.format(self.Cal.__dict__[cn])
            print(self.ids[gn].text)
        
        #import pdb; pdb.set_trace()
        
    pass
    
    

class CalApp(App):
    def build(self):
        return hspc_MachineParameters()


if __name__ == '__main__':
    AppInst=CalApp()
    AppInst.run()
