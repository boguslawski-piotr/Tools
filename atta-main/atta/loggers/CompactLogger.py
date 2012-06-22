import StdLogger

class Logger(StdLogger.Logger):
  '''
  .. snippet:: loggers.CompactLogger
  
    Compact logger.
     
    This logger omits output of empty target output.
  '''
  def __init__(self):
    self.targetName = ''
  
  def Log(self, msg, **args):
    _msg = self._HandleBuild(msg, **args) or self._HandleTask(msg, **args)
    
    if _msg is None:
      if 'target' in args: 
        if 'prepare' in args: 
          self.targetName = self._HandleTarget(msg, **args)
      
    if _msg is None:
      _msg = '{0}'.format(msg)
      
    if _msg and len(self.targetName) > 0:
      self._PhysicalLog(self.targetName)
      self.targetName = ''
      
    self._PhysicalLog(_msg)
    return
