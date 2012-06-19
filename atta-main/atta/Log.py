import sys
import StdLogger
import OS

## Class that allows the dynamic selection logging implementation.
class LoggerBridge:
  ## \privatesection
  
  _loggerClass = StdLogger.Logger
  _logger = None
  
  ## \publicsection

  @staticmethod
  def SetLoggerClass(loggerClass):
    oldloggerClass = LoggerBridge._loggerClass
    if isinstance(loggerClass, basestring):
      print sys.modules[OS.RemoveExt(loggerClass)].__dict__
      print OS.RemoveExt(loggerClass)
      print OS.Ext(loggerClass)
      LoggerBridge._loggerClass = sys.modules[OS.RemoveExt(loggerClass)].__dict__[OS.Ext(loggerClass, False)]
    else:
      LoggerBridge._loggerClass = loggerClass
    LoggerBridge._logger = None
    return oldloggerClass
  
  @staticmethod
  def GetLogger():
    return LoggerBridge._logger
  
  @staticmethod
  def Log(msg, **args):
    if LoggerBridge._logger is None:
      LoggerBridge._logger = LoggerBridge._loggerClass()
    LoggerBridge._logger.Log(msg, **args)
#}
        
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
#}
  
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
  
