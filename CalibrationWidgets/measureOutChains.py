from   kivy.uix.gridlayout                import   GridLayout
from kivy.properties                      import   ObjectProperty, StringProperty
from kivy.clock                           import   Clock
from   kivy.app                           import   App

class MeasureOutChains(GridLayout):
    '''
    
    Provides a standard interface for measuring out a known length of both chains
    
    '''
    data              =  ObjectProperty(None) #set externally
    text              =  StringProperty("")
    countDownTime     =  0
    
    def on_Enter(self):
        '''
        
        This function runs when the step is entered
        
        '''
        self.data = App.get_running_app().data
        self.text =  "Now we are going to measure out the chains and reattach the sled\n\nHook the first link of the right chain on the vertical tooth of the right sprocket\n as shown in the picture below\n\nThe left chain does not need to be moved, it can be left partly extended\n\nThe correct length of first the left and then the right chain will be measured out\n\nOnce both chains are finished attach the sled, then press Next\nPressing Next will move the sled to the center of the sheet.\n\nBe sure to keep an eye on the chains during this process to ensure that they do not become tangled\naround the sprocket. The motors are very powerful and the machine can damage itself this way"
        
        #select the right image for a given setup
        print "measure out chains on enter"
        if App.get_running_app().data.config.get('Advanced Settings', 'chainOverSprocket') == 'Top':
            print "top feeding detected"
            self.leftImg.source = "./Documentation/Calibrate Machine Dimensions/topfeeding/Ready To Calibrate.jpg"
        else :
            print "bottom feeding detected"
            self.leftImg.source = "./Documentation/Calibrate Machine Dimensions/bottomfeeding/Ready To Calibrate.jpg"
    
    def stop(self):
        self.data.quick_queue.put("!") 
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
    
    def next(self):
        self.data.gcode_queue.put("B15 ")
        self.on_Exit()
    
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
    
    def on_Exit(self):
        '''
        
        This function runs when the step is completed
        
        '''
        
        self.readyToMoveOn()