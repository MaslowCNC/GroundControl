from kivy.app import App
from kivy.properties import OptionProperty, NumericProperty, ListProperty, \
        BooleanProperty, StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse
from kivy.graphics import InstructionGroup
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition


class FrontPage(Screen):
    exploreplot = ObjectProperty(None)
    exampleplot = ObjectProperty(None)
    
    def testFuncOne(self):
        print "func one"
        
    def testFuncTwo(self):
        print "func two"

class OtherFeatures(Screen):
    pass

class SoftwareSettings(Screen):
    pass

class GroundControlApp(App):
    def build(self):
        interface = FloatLayout()
        
        screenControls = GridLayout(rows = 1)
        btn1 = Button(text='Front Page', size_hint=(None, None), width = 320, height = 30)
        btn1.bind(on_press=self.showFront)
        screenControls.add_widget(btn1)
        
        btn2 = Button(text='Other Features', size_hint=(None, None), width = 320, height = 30)
        btn2.bind(on_press=self.showFeatures)
        screenControls.add_widget(btn2)
        
        
        btn3 = Button(text='Settings', size_hint=(None, None), width = 320, height = 30)
        btn3.bind(on_press=self.showSettings)
        screenControls.add_widget(btn3)
        
        interface.add_widget(screenControls)
        
        
        self.sm = ScreenManager(transition=SlideTransition(), size_hint=(None, None), pos = (120,0), width = Window.width-120, height = Window.height, clearcolor=(1,1,1,1))
        
        self.frontpage = FrontPage(name='FrontPage')
        self.sm.add_widget(self.frontpage)
        
        self.otherfeatures = OtherFeatures(name='OtherFeatures')
        self.sm.add_widget(self.otherfeatures)
        
        self.softwaresettings = SoftwareSettings(name='SoftwareSettings')
        self.sm.add_widget(self.softwaresettings)
        
        interface.add_widget(self.sm)
        
        return interface

    def showFront(self, extra):
        self.sm.current = 'FrontPage'
    def showFeatures(self, extra):
        self.sm.current = 'OtherFeatures'
    def showSettings(self, extra):
        self.sm.current = 'SoftwareSettings'
    
if __name__ == '__main__':
    GroundControlApp().run()
