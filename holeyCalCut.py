#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 02:57:13 2019

@author: Joshua Schmitt
"""
from   kivy.properties                                      import  ObjectProperty
from   kivy.uix.widget                                      import  Widget
from   CalibrationWidgets.HoleyCalibration                  import  HoleyCalibration
from   kivy.app                                             import  App

class HoleyCalCut(Widget):
    readyToMoveOn=ObjectProperty(None)
    def cutHoleyCalPattern(self):
        data=App.get_running_app().data
        self.Cal.CutTestPattern(data)
    def __init__(self,Dict):
        self.Dict=Dict
        if not 'CalObj' in Dict.keys():
            super(HoleyCalCut,self).__init__()
            self.Cal=HoleyCalibration()
            self.Cal.InitializeIdealXyCoordinates()
            self.Dict.update({'CalObj':self.Cal})
        else:
            self.Cal=Dict['CalObj']
    def on_Enter(self):
        pass
    def on_Exit(self):
        pass
    