'''
Various interfaces.
'''

class ILogger():
  '''
  Logger interface  
  
  special arguments
  
  project
    start
    end
    status
    at
    time
    
  target
    prepare
    start
    end
    finalize
    
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