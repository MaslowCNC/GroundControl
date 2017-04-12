'''

This module provides a logger which can be used to record and later report the machine's 
behavior.

'''

from DataStructures.makesmithInitFuncs       import MakesmithInitFuncs


class Logger(MakesmithInitFuncs):
    
    errorValues = []
    recordingPositionalErrors = False 
    
    def writeToLog(self, message):
        '''
        
        Writes an error message into the log.
        
        '''
        pass
    
    def writeErrorValueToLog(self, error):
        '''
        
        Writes an error value into the log.
        
        '''
        if self.recordingPositionalErrors:
            self.errorValues.append(error)
        
        #if we've gotten to the end of the file
        if self.data.gcodeIndex == len(self.data.gcode) and self.recordingPositionalErrors:
            self.endRecordingAvgError()
            self.reportAvgError()
    
    def beginRecordingAvgError(self):
        '''
        
        Begins recording error values.
        
        '''
        self.recordingPositionalErrors = True
        self.errorValues = []
    
    def endRecordingAvgError(self):
        '''
        
        Stops recording error values.
        
        '''
        print "stopping to record"
        self.recordingPositionalErrors = False
    
    def reportAvgError(self):
        '''
        
        Reports the average positional error since the recording began.
        
        '''
        
        avg = sum(self.errorValues)/len(self.errorValues)
        self.data.message_queue.put("Message: The average feedback system error was: " + "%.2f" % avg + "mm")
        
        
        #should popup message here