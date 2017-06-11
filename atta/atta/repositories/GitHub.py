""".. Remote: TODO"""
import os
import urllib2

from ..tools.internal.Misc import ObjectFromClass
from .. import AttaError, OS, Dict, LogLevel
from . import Remote, Http
from . import Styles

class Repository(Http.Repository):
  """TODO: description"""
  def __init__(self, **tparams):
    if Dict.url not in tparams: tparams[Dict.url] = 'https://github.com'
    Http.Repository.__init__(self, **tparams)
    self._styleImpl = ObjectFromClass(Styles.GitHub)

  def FileExists(self, fileName):
    url = self.Url() + os.path.dirname(fileName)
    try:
      urllib2.urlopen(url, timeout = self.timeout).close()
      return True
    except urllib2.URLError as E:
      return False

  def GetFileMarker(self, fileName, forGet):
    return None, None

  def GetInfoFileContents(self, package, forGet):
    return None

  def _Name(self):
  #    name = Task._Name(self)
  #    return 'Http.' + name
    return 'GitHub'
