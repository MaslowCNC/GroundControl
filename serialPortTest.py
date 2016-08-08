print "it launches"

import kivy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label

from Connection.serialPort   import SerialPort
import time
from DataStructures.data     import Data




class MyApp(App):
    
    data = Data()

    serialWidget = SerialPort()
    serialWidget.setUpData(data)
    
    def build(self):
        return Label(text='Hello world')


if __name__ == '__main__':
    MyApp().run()