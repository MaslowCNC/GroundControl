from kivy.app import App
from kivy.properties import OptionProperty, NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse
from kivy.graphics import InstructionGroup
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from math import cos, sin


class AnalysisOverview(FloatLayout):
    exploreplot = ObjectProperty(None)
    exampleplot = ObjectProperty(None)
    
    def testFuncOne(self):
       print "func one"
        
    def testFuncTwo(self):
        print "func two"

class GroundControlApp(App):
    def build(self):
        interface =  AnalysisOverview()
        return interface


if __name__ == '__main__':
    GroundControlApp().run()
