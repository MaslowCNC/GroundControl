from kivy.app               import App

from kivy.uix.scatter       import Scatter
from kivy.uix.label         import Label
from kivy.uix.button        import Button
from kivy.uix.floatlayout   import FloatLayout
from kivy.uix.textinput     import TextInput
from kivy.uix.boxlayout     import BoxLayout
from kivy.graphics          import Color, Ellipse, Line, Rectangle

class TutorialApp(App):
    def build(self):
        boxLayoutInstance        = BoxLayout(orientation='vertical')
        floatLayoutInstance      = FloatLayout()
        scatterObject            = Scatter()
        ScatterableObject        = Label(text='Hello world', font_size=14)
        with ScatterableObject.canvas:
            Color(1, 1, 1)
            Line(points = (0, 0, 100, 100))

        floatLayoutInstance.add_widget(scatterObject)
        scatterObject.add_widget(ScatterableObject)

        boxLayoutInstance.add_widget(floatLayoutInstance)
        return boxLayoutInstance

if __name__ == "__main__":
    TutorialApp().run()