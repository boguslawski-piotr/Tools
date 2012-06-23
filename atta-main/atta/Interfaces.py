'''
Various interfaces.
'''

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
    finalize
    msg
    
  task
  ''' 
  def Log(self, msg, **args):
    pass
  
class IVariablesExpander:
  '''
  IVariablesExpander interface
  
  TODO: description
  '''
  def Expand(self, txt, **tparams): 
    pass  