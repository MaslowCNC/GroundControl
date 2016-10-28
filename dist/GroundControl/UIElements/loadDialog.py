from kivy.uix.floatlayout    import    FloatLayout
from kivy.properties         import    ObjectProperty


class LoadDialog(FloatLayout):
    '''
    
    A Pop-up Dialog To Open A File
    
    '''
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)