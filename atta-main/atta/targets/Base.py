""".. no-user-reference:"""
import os
import platform

from ..tools.Interfaces import AbstractMethod, IsAbstractMethod
from ..Activity import Activity
from .. import OS
from .. import Dict

class Target(Activity):
  """
  Base class for all targets.

  TODO: description
  """

  #: DOCTODO: description
  dependsOn = []

  #: DOCTODO: description
  system = []

  def CanRun(self):
    """TODO: description"""
    canRun = True
    if len(self.system) > 0:
      canRun = False
      system = platform.system().lower()
      tsystem = OS.Path.AsList(self.system, ',')
      for s in tsystem:
        if s.lower() in system:
          canRun = True
          break
    return canRun

  @AbstractMethod
  def Prepare(self):
    """Method 'Prepare' can be defined in a class that inherits from the Target.
       Then will start. When it returns False, project will not run any targets from
       the section 'dependsOn' as well as the Run method."""
    assert False

  @AbstractMethod
  def Run(self):
    """TODO: description"""
    assert False

  @AbstractMethod
  def Finalize(self):
    """Method 'Finalize' can be defined in a class that inherits from the Target.
       Then will start right after a successful finish the Run method."""
    assert False

  # private section

  def _Type(self):
    return Dict.target

  def _Name(self):
    if not hasattr(self, 'name'):
      self.name = '{0}'.format(self.__class__)
      self.name = self.name.replace('atta.targets.', '')
      project = self.Project
      if project and project._parent is None:
        self.name = self.name.replace(OS.Path.RemoveExt(os.path.basename(project.fileName)) + '.', '')
    return self.name

  def _RunPrepare(self):
    if not IsAbstractMethod(self.Prepare):
      self._Log(prepare = True)
      return self.Prepare()
    return True

  def _Run(self):
    if not hasattr(self, 'wasExecuted') or not self.wasExecuted:
      self._Log(start = True)
      self.Run()
      self._Log(end = True)
    self.wasExecuted = True

  def _RunFinalize(self):
    if not IsAbstractMethod(self.Finalize):
      self._Log(finalize = True)
      self.Finalize()
