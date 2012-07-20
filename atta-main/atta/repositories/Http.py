""".. Remote: TODO"""
import urllib2

from .. import AttaError, OS, Dict, LogLevel
from . import Local
from . import Remote

class Repository(Remote.Repository):
  """TODO: description"""
  def __init__(self, **tparams):
    Remote.Repository.__init__(self, **tparams)

    self.url = self.data.get(Dict.url)
    if not self.url:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.url))
    if not self.url.endswith('/'):
      self.url += '/'

    if not self.rootDirName:
      self.rootDirName = ''

  def NormPath(self, path):
    return OS.Path.NormUnix(path)

  def MakeDirs(self, dirName):
    assert False

  def FileExists(self, fileName):
    url = self.Url() + fileName
    try:
      urllib2.urlopen(url).close()
      return True
    except urllib2.URLError as E:
      return False

  def FileTime(self, fileName):
    assert False

  def FileHash(self, fileName):
    return None

  def Touch(self, fileName):
    pass

  def GetFileLike(self, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgDownloadingFile % fileName, level = logLevel)
    url = self.Url() + fileName
    return urllib2.urlopen(url)

  def PutFileLike(self, f, fileName, logLevel = LogLevel.VERBOSE):
    assert False

  def PutFile(self, srcFileName, destFileName, logLevel = LogLevel.VERBOSE):
    assert False

  def PutFileContents(self, contents, fileName, logLevel = LogLevel.DEBUG):
    assert False

  def Url(self):
    return self.url

  def CompleteFileName(self, fileName):
    return fileName

  def DefaultStore(self):
    return Local.Repository()

  def Check(self, package, scope):
    assert False

  def Put(self, fBaseDirName, files, package):
    assert False

  def _Name(self):
  #    name = Task._Name(self)
  #    return 'Http.' + name
    return 'Http'
