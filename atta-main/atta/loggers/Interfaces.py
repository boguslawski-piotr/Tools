import os
import atta.tools.OS as OS

class ILogger:
  '''
  Logger interface  
  
  special arguments
  
  project
    start
    end
    msg
    
    status
    at
    time
    exception
    
  target
    prepare
    start
    end
    msg
    
  task
  ''' 
  def Log(self, msg, **args):
    pass
  
    