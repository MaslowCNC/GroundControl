from kivy.properties      import StringProperty
from kivy.uix.button          import Button

class ButtonTemplate(Button):
    btnBackground     = StringProperty('atlas://data/images/defaulttheme/button')
    btnBackgroundDown = StringProperty('atlas://data/images/defaulttheme/button_pressed')
    
