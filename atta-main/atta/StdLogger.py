import os
from Interfaces import ILogger

## Default logger.
class Logger(ILogger):
  def Log(self, msg, **args):
    _msg = self._HandleBuild(msg, **args) or self._HandleTarget(msg, **args) or self._HandleTask(msg, **args)
    if _msg is None:
      _msg = '{0}'.format(msg)
    self._PhysicalLog(_msg)
    return
  
  ## \privatesection
  
  def _PhysicalLog(self, msg):
    if msg:
      print(msg)
      
  def _HandleBuild(self, msg, **args):
    if 'project' in args:
      if 'start' in args:
        pass
      if 'end' in args:
        _msg =        '\nBuild: {0}'.format(args['status'])
        _msg = _msg + '\n   At: {0}'.format(args['at'].isoformat())
        _msg = _msg + '\n Time: {0}'.format(args['time'])
        if 'exception' in args:
          _msg = _msg + '\n'
        return _msg
    return None

  def _HandleTarget(self, msg, **args):
    if 'target' in args: 
      if 'prepare' in args:
        _msg = os.linesep + args['target'] + ':'
        return _msg
    return None

  def _HandleTask(self, msg, **args):
    if 'task' in args:
      _msg = '{0}'.format(msg)
      lines = _msg.replace('\r', '').split('\n')
      _msg = ''
      for line in lines:
        if len(_msg) > 0:
          _msg = _msg + os.linesep
        _msg = _msg + "{0:>8}: {1}".format(args['task'], line)
      return _msg
    return None

