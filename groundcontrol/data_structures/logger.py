'''

This module provides a logger which can be used to record and later report the machine's 
behavior.

'''

from groundcontrol.data_structures.makesmithInitFuncs       import MakesmithInitFuncs
import threading


class Logger(MakesmithInitFuncs):
    
    errorValues = []
    recordingPositionalErrors = False 
    
    messageBuffer = ""
    
    #clear the old log file
    with open("log.txt", "a") as logFile:
            logFile.truncate()
    
    def writeToLog(self, message):
        '''
        
        Writes a message into the log
        
        Actual writing is done in a separate thread to no lock up the UI because file IO is 
        way slow
        
        '''
        
        try:
            self.messageBuffer = self.messageBuffer + message
        except:
            pass
        
        if len(self.messageBuffer) > 500:
            
            t = threading.Thread(target=self.writeToFile, args=(self.messageBuffer, "write"))
            t.daemon = True
            t.start()
            self.messageBuffer = ""
    
    def writeToFile(self, toWrite, *args):
        '''
        
        Write to the log file
        
        '''
        
        with open("log.txt", "a") as logFile:
            logFile.write(toWrite)
        
        return
        
    def writeErrorValueToLog(self, error):
        '''
        
        Writes an error value into the log.
        
        '''
        if self.recordingPositionalErrors:
            self.errorValues.append(abs(error))
        
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
        print("stopping to record")
        self.recordingPositionalErrors = False
    
    def reportAvgError(self):
        '''
        
        Reports the average positional error since the recording began.
        
        '''
        
        avg = sum(self.errorValues)/len(self.errorValues)
        self.data.message_queue.put("Message: The average feedback system error was: " + "%.2f" % avg + "mm")
        
        
        #should popup message here