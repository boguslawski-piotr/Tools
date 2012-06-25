'''
Various interfaces and base classes.
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
  
#------------------------------------------------------------------------------ 

import atta

class Activity:
  '''
  Base class for all targets, tasks and other executive classes.
     
  TODO: description
  '''
  def Log(self, msg = '', **args):
    self._Log(msg, **args)

  def LogIterable(self, msg = '', iterable = [], **args):
    self._LogIterable(msg, iterable, **args)
  
  '''private section'''
    
  def _Type(self):
    return ''

  def _Name(self):
    return ''
  
  def _Log(self, msg = '', **args):
    args[self._Type()] = self._Name()
    atta.Atta.logger.Log(msg, **args)

  def _LogIterable(self, msg = '', iterable = [], **args):
    args[self._Type()] = self._Name()
    atta.Atta.logger.LogIterable(msg, iterable, **args)
