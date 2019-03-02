#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 15:22:46 2019

@author: Joshua Schmitt
"""

from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.app import App

def LoadCalibrateWid():
    BaseStr= \
"""
<HoleyCalOptimize>:
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
                    on_release: root.pushParamsToGC()
                Button:
                    size_hint_x: .5
                    text: 'Next'
                    on_release: root.readyToMoveOn()"""
    WidLayout=''.join([BaseStr,Labels,mmts,CalBox,lblstr,prms,ptm])
    Builder.load_string(WidLayout)
    
    
LoadCalibrateWid()

class HoleyCalOptimize(Widget):
    def __init__(self,Dict):
        super(HoleyCalOptimize,self).__init__()
        self.Dict=Dict
        # Tuple format:
        #       (Firmware Key group,  Firmware Key Name,   Key, Start Holey Cal Name,     End Holey Cal Name,       GUI ID)
        self.KeyMap=[
                ('Advanced Settings','rotationRadius',     8,   'SP_rotationDiskRadius', 'SP_rotationDiskRadius',  'RotRad'),
                ('Advanced Settings','leftChainTolerance', 40,  'SP_leftChainTolerance', 'Opt_leftChainTolerance', 'InitLftChTol'),
                ('Advanced Settings','rightChainTolerance',41,  'SP_rightChainTolerance','Opt_rightChainTolerance','InitRghtChTol'),
                ('Advanced Settings','chainOverSprocket',  None,'SP_chainOverSprocket',  'SP_chainOverSprocket',   'ChainOverSprocket'),
                ('Maslow Settings',  'motorOffsetY',       3,   'SP_motorOffsetY',       'Opt_motorOffsetY',       'InitMotorYOffset'),
                ('Advanced Settings','chainSagCorrection', 37,  'SP_sledWeight',         'SP_sledWeight',          'SledWeight'),
                ('Maslow Settings',  'motorSpacingX',      2,   'SP_D',                  'Opt_D',                  'InitDistBtwnMtrs'),
                ('Advanced Settings','kinematicsType',     None,'isQuadKinematics',      'isQuadKinematics',       'IsQuadKin')]
    def on_Enter(self):
        self.data=App.get_running_app().data
        Dict=self.Dict
        cal=Dict['CalObj']
#        PrmIds=['MotorYOffset','DistBtwnMtrs','LftChTol','RghtChTol']
#        InitIds=['Init{0}'.format(pid) for pid in PrmIds]
#        CalIds=['Cal{0}'.format(cid) for cid in PrmIds]
        
        
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
        
        #Calibrated Machine Parameters
        #       (Firmware Key group,  Firmware Key Name,   Key, Start Holey Cal Name,     End Holey Cal Name,       GUI ID)
        for grp,fnm,fky,shcnm,ehcnm,iid in self.KeyMap:
            v=self.data.config.get(grp,fnm)
            if iid in self.ids:
                self.ids[iid].text=v
            
            if iid == 'ChainOverSprocket':
                v=v=='Top'
            elif iid == 'IsQuadKin':
                v=v=='Quadrilateral'
            else:
                v=float(v)
            cal.__dict__[shcnm]=v
            
#        CalNames=\
#            [('isQuadKinematics','IsQuadKin'),\
#             ('SP_D','DistBtwnMtrs'),\
#             ('SP_motorOffsetY','MotorYOffset'),\
#             ('SP_rotationDiskRadius','RotRad'),\
#             ('SP_leftChainTolerance','LftChTol'),\
#             ('SP_rightChainTolerance','RghtChTol'),\
#             ('SP_chainOverSprocket','ChainOverSprocket'),\
#             ('SP_sledWeight','SledWeight')]
#        for cn,dn in CalNames:
#            if Dict[dn]:
#                cal.__dict__[cn]=float(Dict[dn])
#            else:
#                cal.__dict__[cn]=0.0
        #import pdb; pdb.set_trace()
        cal.kin.isQuadKinematics=bool(cal.isQuadKinematics)
        cal.InitializeIdealXyCoordinates()
        self.Cal=cal
        
        
    def on_Exit(self):
        pass
        
        
    def Calibrate(self):
        self.Cal.Calibrate()
        self.CalibratedLengthsToGui()
        self.Cal.ReportCalibration()
        
    def CalibratedLengthsToGui(self):
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
        
    def pushParamsToGC(self):
        #Calibrated Machine Parameters
        for grp,fnm,fky,shcnm,ehcnm,iid in self.KeyMap:
            v=self.Cal.__dict__[ehcnm]            
            if iid == 'ChainOverSprocket':
                if v:
                    v='Top'
                else:
                    v='Bottom'
            elif iid == 'IsQuadKin':
                if v:
                    v='Quadrilateral'
                else:
                    v='Triangular'
            else:
                v=str(v)
            self.data.config.set(grp,fnm,v)
