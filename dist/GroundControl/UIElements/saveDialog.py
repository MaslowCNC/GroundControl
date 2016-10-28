from kivy.uix.floatlayout    import    FloatLayout
from kivy.properties         import    ObjectProperty


class SaveDialog(FloatLayout):
    '''
    
    A Pop-up Dialog To Save A File
    
    '''
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
