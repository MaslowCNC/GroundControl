from kivy.uix.label         import Label
from kivy.uix.scrollview    import ScrollView
from kivy.properties        import StringProperty

class ScrollableLabel(ScrollView):
    '''
    
    Creates a label which has the property that if the text is wider than the label
    the text will wrap, and if it is taller than the label, a scroll bar will be added
    
    '''
    text = StringProperty('')