from Bridge import Bridge
from loggers import StdLogger
        
class LogLevel:
  '''
  Defines the available log levels and stores the global log level.
  '''
   
  DEBUG = 0
  VERBOSE = 1
  INFO = 2
  WARNING = 3
  ERROR = 4
  
  actual = INFO
  '''Actual log level.'''
  
  @staticmethod
  def LogAllowed(level):
    '''Returns True if log is enabled for specified `level`.'''
    return level >= LogLevel.actual
  
_logger = Bridge(StdLogger.Logger)

def SetLogger(_class):
  '''
  TODO: description
  '''
  return _logger.SetClass(_class)
    
def Log(msg, **args):
  '''
    Sends message and parameters to the log.
    More information about logs can be found 
    in :py:class:`atta.Interfaces.ILogger`.
  ''' 
  level = args.get('level', LogLevel.INFO)
  if LogLevel.LogAllowed(level):
    _logger.GetImpl().Log(msg, **args)

def LogNM(**args):
  '''
    Sends parameters to the log.
    More information about logs can be found 
    in :py:class:`atta.Interfaces.ILogger`.
  ''' 
  Log('', **args)
  
