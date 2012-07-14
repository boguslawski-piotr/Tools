'''
TODO: description
'''
__all__ = [
           'LogLevel',
           'Logger',
          ]

class LogLevel:
  '''Defines the available log levels.'''
  DEBUG = 0
  VERBOSE = 1
  INFO = 2
  WARNING = 3
  ERROR = 4

  @staticmethod
  def Default():
    '''Returns default Atta log level.'''
    return LogLevel.INFO

from ..tools.internal.Misc import ObjectFromClass
from .. import Dict
from ..tools.Misc import isiterable

class Logger:
  '''
  TODO: description
  '''
  def __init__(self, _class):
    self._logLevel = LogLevel.Default()
    self._logger = ObjectFromClass(_class)
    self._listeners = []

  def SetImpl(self, _class):
    '''Sets physical logger class and returns previous class.'''
    return self._logger.SetClass(_class)

  def RegisterListener(self, _class):
    '''TODO: description'''
    listener = ObjectFromClass(_class)
    self._listeners.append(listener)
    return listener

  def UnRegisterListener(self, listener):
    '''TODO: description'''
    i = self._listeners.index(listener)
    del self._listeners[i]

  def Log(self, msg = '', **args):
    '''
    Sends message and parameters to the log and 
    all registered listeners.
    More information can be found in 
    :py:class:`atta.tools.Interfaces.ILogger`.
    '''
    level = args.get(Dict.paramLevel, LogLevel.Default())
    if self.LogAllowed(level):
      self._logger.GetObject().Log(msg, **args)
      for listener in self._listeners:
        listener.GetObject().Log(msg, **args)

  def L(self, msg = '', **args):
    '''Shortcut for Log.'''
    self.Log(msg, **args)

  def LogIterable(self, msg, iterable, **args):
    '''TODO: description'''
    level = args.get(Dict.paramLevel, LogLevel.Default())
    if self.LogAllowed(level):
      if msg is not None:
        self.Log(msg, **args)
      _depth = args.get('_depth', 2)
      if isinstance(iterable, dict):
        for n, v in iterable.items():
          if isiterable(v):
            self.LogIterable(' ' * _depth + n + ':', v, _depth = _depth + 2, **args)
          else:
            self.Log(' ' * _depth + '{0}: {1}'.format(n, v), **args)
      else:
        for v in iterable:
          if isiterable(v):
            self.LogIterable(None, v, _depth = _depth + 2, **args)
          else:
            self.Log(' ' * _depth + '{0}'.format(v), **args)

  def LI(self, msg, iterable, **args):
    '''Shortcut for LogIterable.'''
    self.LogIterable(msg, iterable, **args)

  def SetLevel(self, level):
    '''Sets actual log level.'''
    self._logLevel = level

  def GetLevel(self):
    '''Gets actual log level.'''
    return self._logLevel

  def LogAllowed(self, level):
    '''Returns True if log is enabled for specified `level`.'''
    return level >= self.GetLevel()
