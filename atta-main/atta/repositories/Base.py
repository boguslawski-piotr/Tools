""".. no-user-reference:"""
from ..tools.internal.Misc import ObjectFromClass
from ..tools.Interfaces import AbstractMethod
from .. import Dict
from . import Styles

class ARepository:
  """TODO: description"""
  def __init__(self, data):
    self.data = data
    if data:
      _styleClass = data.get(Dict.style, ARepository.GetDefaultStyleImpl())
    else:
      self.data = {}
      _styleClass = ARepository.GetDefaultStyleImpl()
    self._styleImpl = ObjectFromClass(_styleClass)

  _defaultStyleImpl = ObjectFromClass(Styles.Maven)

  @staticmethod
  def SetDefaultStyleImpl(_class):
    """TODO: description"""
    ARepository._defaultStyleImpl = ObjectFromClass(_class)

  @staticmethod
  def GetDefaultStyleImpl():
    """TODO: description"""
    return ARepository._defaultStyleImpl.GetClass()

  # Properties

  def SetOptionalAllowed(self, v):
    """TODO: description"""
    self.data[Dict.getOptional] = v

  def OptionalAllowed(self):
    """Returns `True` if optional packages allowed for repository instance.
    TODO: more description"""
    return self.data.get(Dict.getOptional, False)

  # Abstract methods (interface)

  @AbstractMethod
  def Get(self, package, scope, store = None):
    """TODO: description"""
    assert False

  @AbstractMethod
  def Check(self, package, scope):
    """TODO: description"""
    assert False

  @AbstractMethod
  def Put(self, fBaseDirName, files, package):
    """TODO: description"""
    assert False

  @AbstractMethod
  def Clean(self, package):
    """TODO: description"""
    assert False

  @AbstractMethod
  def _Name(self):
    """TODO: description"""
    assert False
