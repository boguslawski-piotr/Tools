
## Class that allows the dynamic selection logging implementation.
class LoggerBridge:
  LoggerClass = None

  @staticmethod
  def Log(msg, **args):
    LoggerBridge.LoggerClass().Log(msg, **args)
        
## Defines the available log levels. 
class LogLevel:
  DEBUG = 0
  VERBOSE = 1
  INFO = 2
  WARNING = 3
  ERROR = 4
  
  ## Actual log level.
  actual = INFO
  
  ## Returs True if log is enabled for specified \p level.
  @staticmethod
  def LogAllowed(level):
    return level >= LogLevel.actual
  
## Sends message and parameters to the log.
#  More information about logs can be found 
#  in \link atta.Interfaces.ILogger \endlink. 
def Log(msg, **args):
  level = args.get('level', LogLevel.INFO)
  if LogLevel.LogAllowed(level):
    LoggerBridge.Log(msg, **args)

## Sends parameters to the log.
#  More information about logs can be found 
#  in \link atta.Interfaces.ILogger \endlink. 
def LogNM(**args):
  Log('', **args)
  
