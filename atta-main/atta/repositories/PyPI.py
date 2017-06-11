""".. Remote: TODO"""

from ..tools.internal.Misc import ObjectFromClass
from .. import AttaError, OS, Dict, LogLevel
from . import Http
from . import Styles

class Repository(Http.Repository):
  """TODO: description"""
  def __init__(self, **tparams):
    if Dict.url not in tparams: tparams[Dict.url] = 'http://pypi.python.org'
    Http.Repository.__init__(self, **tparams)
    self._styleImpl = ObjectFromClass(Styles.PyPI)

  def GetFileMarker(self, fileName, forGet):
    return None, None

  def GetInfoFileContents(self, package, forGet):
    return None

  def _Name(self):
  #    name = Task._Name(self)
  #    return 'Http.' + name
    return 'PyPI'
