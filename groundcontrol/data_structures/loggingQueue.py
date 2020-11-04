'''

This module provides a simple addition to the Queue, which is that it logs
puts to the Queue immediately.

'''

from queue import Queue


class LoggingQueue(Queue, object):
    def __init__(self, logger):
        self.logger = logger
        super(LoggingQueue, self).__init__()
    
    def put(self, msg):
        self.logger.writeToLog(msg)
        return super(LoggingQueue, self).put(msg)
    