from atta import StdLogger

## Compact logger.
#  This logger omits output of empty target output.
class Logger(StdLogger.Logger):
  targetName = ''
  
  def Log(self, msg, **args):
    _msg = self._HandleBuild(msg, **args) or self._HandleTask(msg, **args)
    
    if _msg is None:
      if 'target' in args: 
        if 'prepare' in args: Logger.targetName = self._HandleTarget(msg, **args)
      
    if _msg is None:
      _msg = '{0}'.format(msg)
      
    if _msg and len(Logger.targetName) > 0:
      self._PhysicalLog(Logger.targetName)
      Logger.targetName = ''
      
    self._PhysicalLog(_msg)
    return
