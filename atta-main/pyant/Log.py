
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
global logLevel
logLevel = LogLevel.INFO

## Sends message and parameters to the log.
#  More information about logs can be found 
#  in \link pyant.Interfaces.ILogger \endlink. 
def Log(msg, **args):
  level = args.get('level', LogLevel.INFO)
  if _LogAllowed(level):
    LoggerBridge.Log(msg, **args)

## Sends parameters to the log.
#  More information about logs can be found 
#  in \link pyant.Interfaces.ILogger \endlink. 
def LogNM(**args):
  Log('', **args)
  
def _LogAllowed(level):
  return level >= logLevel
