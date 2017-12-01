from kivy.uix.widget                      import   Widget
from kivy.properties                      import   ObjectProperty, StringProperty
from kivy.clock                           import   Clock

class MeasureOutChains(Widget):
    '''
    
    Provides a standard interface for measuring out a known length of both chains
    
    '''
    data              =  ObjectProperty(None) #set externally
    text              =  StringProperty("")
    countDownTime     =  0
    
    def stop(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def next(self):
        self.data.gcode_queue.put("B15 ")
        self.carousel.load_next()
    
    '''
    Left Chain
    '''
    def startCountDownL(self):
        self.countDownTime  = 5
        
        Clock.schedule_once(self.countingDownL, 1)
        self.leftChainBtn.text = '   Extend\nLeft Chain (' + str(self.countDownTime) + ")"
    
    def countingDownL(self, *args):
        self.countDownTime = self.countDownTime - 1
        
        self.leftChainBtn.text = '   Extend\nLeft Chain (' + str(self.countDownTime) + ")"
        
        if self.countDownTime > 0:
            Clock.schedule_once(self.countingDownL, 1)
        else:
            self.leftChainBtn.text = '   Extend\nLeft Chain'
            self.data.gcode_queue.put("B02 L1 R0 ")
    
    '''
    Right Chain
    '''
    
    def startCountDownR(self):
        self.countDownTime  = 5
        
        Clock.schedule_once(self.countingDownR, 1)
        self.rightChainBtn.text = '   Extend\nRight Chain (' + str(self.countDownTime) + ")"
    
    def countingDownR(self, *args):
        self.countDownTime = self.countDownTime - 1
        
        self.rightChainBtn.text = '   Extend\nRight Chain (' + str(self.countDownTime) + ")"
        
        if self.countDownTime > 0:
            Clock.schedule_once(self.countingDownR, 1)
        else:
            self.rightChainBtn.text = '   Extend\nRight Chain'
            self.data.gcode_queue.put("B02 L0 R1 ")