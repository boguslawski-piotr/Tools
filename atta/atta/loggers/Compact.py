from . import Std
from .. import Dict

class Logger(Std.Logger):
  """
    Compact logger.

    This logger omits output of empty target output.
  """
  def __init__(self):
    self.targetName = ''

  def Log(self, msg, **args):
    _msg = self._HandleProject(msg, **args) or self._HandleTask(msg, **args)

    if _msg is None:
      if Dict.target in args:
        if 'start' in args or 'prepare' in args:
          self.targetName = self._HandleTarget(msg, **args)

    if Dict.project in args:
      self.targetName = ''

    if _msg is None:
      _msg = '%s' % msg

    if _msg and len(self.targetName) > 0:
      self._PhysicalLog(self.targetName)
      self.targetName = ''

    self._PhysicalLog(_msg)
