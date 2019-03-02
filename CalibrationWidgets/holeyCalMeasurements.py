#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 14:28:22 2019

@author: Joshua Schmitt
"""
from kivy.uix.widget  import Widget
from kivy.properties  import ObjectProperty
from CalibrationWidgets.HoleyCalibration import HoleyCalibration

def get_id(root,instance):
    for id, widget in root.ids.items():
        if widget.__self__ == instance:
            return id

class HoleyCalMeasurements(Widget):
    readyToMoveOn      = ObjectProperty(None)
    DictIds=['M{}'.format(num) for num in range(1,13)]
    def __init__(self,Dict):
        super(HoleyCalMeasurements,self).__init__()
        self.Dict=Dict
        if not 'CalObj' in Dict.keys():
            self.Cal=HoleyCalibration()
            self.Cal.InitializeIdealXyCoordinates()
            self.Dict.update({'CalObj':self.Cal})
        else:
            self.Cal=Dict['CalObj']
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
        
        self.readyToMoveOn()
#        CalWid=hspc_Calibrate(self.Dict)
#        self.clear_widgets()
#        self.parent.add_widget(CalWid)
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
    def on_Enter(self):
        pass
    def on_Exit(self):
        pass
    #def __init__(self,MachineParams):
        #import pdb; pdb.set_trace()
        #self.cal=HoleyCalibration
        #pass