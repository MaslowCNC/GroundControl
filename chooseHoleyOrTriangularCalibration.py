#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 05:57:04 2019

@author: Joshua Schmitt
"""
from   kivy.properties                                      import  ObjectProperty
from   kivy.uix.widget                                      import  Widget

class ChooseHoleyOrTriangularCalibration(Widget):
    readyToMoveOn=ObjectProperty(None)
    def on_Enter(self):
        pass        
    def on_Exit(self):
        pass