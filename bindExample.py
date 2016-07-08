from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import BooleanProperty
from kivy.app                   import App

class Board(GridLayout):
    def __init__(self, **kwargs):
        super(Board, self).__init__(**kwargs)
        for i in range(10):
            self.add_widget(Square())
        for square in self.children:
            print square
            square.bind(occupied=self.do_a_thing)

    def do_a_thing(self, *args):
        print "hello from {}, new state: {}".format(*args)
        for square in self.children:
            pass
            #do a thing

class Square(Button):
     occupied = BooleanProperty(False)
    # def on_occupied(self, *args):
    #     print "Callback defined in class: from {} state {}".format(*args)


class mApp(App):
    def build(self):
        return Builder.load_string("""
Board:
    cols: 4
    rows: 3
<Square>:
    on_press: self.occupied = ~self.occupied
""")
mApp().run()