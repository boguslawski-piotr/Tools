'''TODO: description'''

from .tools.Misc import LogLevel, isiterable
from . import Dict
from . import Atta

class Activity:
  '''
  Base class for all targets, tasks and other executive classes.
     
  TODO: description
  '''
  def LogLevel(self):
    return Atta.LogLevel()
  
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
    Atta.Log(msg, **args)

  def _LogIterable(self, msg = '', iterable = [], **args):
    args[self._Type()] = self._Name()
    Atta.LogIterable(msg, iterable, **args)

  def _DumpParams(self, locals_):
    if Atta.LogLevel() == LogLevel.DEBUG:
      self.Log(Dict.msgDumpParameters)
      for name, value in locals_.items():
        if name != 'self':
          if isiterable(value):
            self.LogIterable('{0}:'.format(name), value)
          else:
            self.Log('{0}: {1}'.format(name, value))
      self.Log('')
      
    