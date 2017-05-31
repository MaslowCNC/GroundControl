from kivy.uix.floatlayout             import    FloatLayout
from kivy.properties                  import    ObjectProperty
from kivy.properties                  import    StringProperty
from UIElements.scrollableLabel       import    ScrollableLabel


class PageableTextPopup(FloatLayout):
    '''
    
    A Pop-up Dialog To Display Text
    
    If the text does not all fit on the display, the user can scroll it
    
    '''
    cancel = ObjectProperty(None)
    next = ObjectProperty(None)
    prev = ObjectProperty(None)
    text = StringProperty("")