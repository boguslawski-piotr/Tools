""".. no-user-reference:"""
import os
from datetime import datetime, timedelta

from ..tools.internal.Misc import ObjectFromClass
from ..tools.Interfaces import AbstractMethod
from .. import Dict
from . import Styles

class ARepository:
  """TODO: description"""
  def __init__(self, **tparams):
    self.data = tparams

    _styleClass = self.data.get(Dict.style, ARepository.GetDefaultStyleImpl())
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

  @staticmethod
  def IsMySubclass(_class):
    try: return issubclass(_class, ARepository)
    except Exception: return False

  @staticmethod
  def IsMyInstance(obj):
    try: return isinstance(obj, ARepository)
    except Exception: return False

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
  def Url(self):
    """TODO: description"""
    assert False

  @AbstractMethod
  def PrepareFileName(self, package):
    """TODO: description"""
    assert False

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
