import os
import atta.tools.OS as OS

class ILogger:
  '''
  Logger interface  
  
  special arguments
  
  project
    start
    end
    log
    
    status
    at
    time
    exception
    
  target
    prepare
    start
    end
    finalize
    log
    
  task
  ''' 
  def Log(self, msg, **args):
    pass
  
    