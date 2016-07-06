from kivy.uix.label         import Label
from kivy.uix.scrollview    import ScrollView
from kivy.properties        import StringProperty

class ScrollableLabel(ScrollView):
    text = StringProperty('')