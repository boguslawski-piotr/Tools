'''
  .. snippet:: Misc
  
    TODO: description
'''
from internal.Misc import ObjectFromClass

#------------------------------------------------------------------------------ 

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

#------------------------------------------------------------------------------ 

class Logger:
  '''
  TODO: description
  '''
  def __init__(self, _class):
    self._logLevel = LogLevel.Default()    
    self._logger = ObjectFromClass(_class)
    self._listeners = []
      
  def SetClass(self, _class):
    '''Sets physical logger class and returns previous class.'''
    return self._logger.SetClass(_class)

  def RegisterListenerClass(self, _class):
    '''TODO: description'''
    listener = ObjectFromClass(_class)
    self._listeners.append(listener)
    return listener
  
  def Log(self, msg = '', **args):
    '''
    Sends message and parameters to the log.
    More information can be found in 
    :py:class:`atta.Interfaces.ILogger`.
    ''' 
    level = args.get('level', LogLevel.Default())
    if self.LogAllowed(level):
      self._logger.GetObject().Log(msg, **args)
      for listener in self._listeners:
        listener.GetObject().Log(msg, **args)
        
  def L(self, msg = '', **args):
    '''Shortcut for Log.'''
    self.Log(msg, **args)
    
  def LogIterable(self, msg = '', iterable = [], **args):
    '''TODO: description'''
    level = args.get('level', LogLevel.Default())
    if self.LogAllowed(level):
      if msg is not None: 
        self.Log(msg, **args)
      for v in iterable:
        self.Log('{0}'.format(v), **args)

  def LI(self, msg = '', iterable = [], **args):
    '''Shortcut for LogIterable'''
    self.Log(msg, **args)
      
  def SetLevel(self, level):
    '''Sets actual log level.'''
    self._logLevel = level

  def GetLevel(self):
    '''Gets actual log level.'''
    return self._logLevel
    
  def LogAllowed(self, level):
    '''Returns True if log is enabled for specified `level`.'''
    return level >= self.GetLevel()

#------------------------------------------------------------------------------ 

class VariablesExpander:
  '''
  TODO: description
  '''
  def __init__(self, _class):
    self._expander = ObjectFromClass(_class)  
    
  def SetClass(self, _class):
    '''Sets variables expander class and returns previous class.'''
    return self._expander.SetClass(_class)
      
  def Expand(self, txt, **tparams):
    '''Expand variables in given text.'''
    return self._expander.GetObject().Expand(txt, **tparams)

