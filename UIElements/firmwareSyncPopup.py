#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 22:38:41 2019

@author: john
"""
from   kivy.uix.popup                            import   Popup

class FirmwareSyncPopup(Popup):
    def __init__(self,GcVal,FwVal,Section,Key):
        super(FirmwareSyncPopup,self).__init__()
        self.GcVal=GcVal
        self.FwVal=FwVal
        self.Section=Section
        self.Key=Key
        self.ids['GcVal'].text=str(GcVal)
        self.ids['FwVal'].text=str(FwVal)
        self.ids['KeyLabel'].text='{}\n{}'.format(Section,Key)
    def SelectGroundControlValue(self):
        self.data.config.set(self.Section,self.Key,self.GcVal)
        self.dismiss()
    def SelectFirmwareValue(self):
        self.data.config.set(self.Section,self.Key,self.FwVal)
        self.dismiss()

if __name__=='__main__':
    fsp=FirmwareSyncPopup(GcVal,FwVal,KeyNum,Key)
    