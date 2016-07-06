from kivy.app               import App
from kivy.uix.label         import Label
from kivy.uix.scrollview    import ScrollView
from kivy.properties        import StringProperty
from kivy.lang              import Builder

long_text = 'yay moo cow foo bar moo baa ' * 100

Builder.load_string('''
<ScrollableLabel>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
''')

class ScrollableLabel(ScrollView):
    text = StringProperty('')

class ScrollApp(App):
    def build(self):
        return ScrollableLabel(text=long_text)

if __name__ == "__main__":
    ScrollApp().run()