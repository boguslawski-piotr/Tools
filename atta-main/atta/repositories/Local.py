'''.. Local: TODO'''
import os
import hashlib
from datetime import datetime, timedelta

from ..tasks.Base import Task
from ..tools.Misc import RemoveDuplicates, NamedFileLike, LogLevel
from ..tools import OS
from .. import AttaError
from .. import Dict
from .Base import ARepository
from .Package import PackageId
from . import ArtifactNotFoundError

def GetPOMFileContents(packageId):
  pass

class Repository(ARepository, Task):
  '''TODO: description'''

  def vMakeDirs(self, dirName):
    OS.MakeDirs(dirName)

  def vFileExists(self, fileName):
    return os.path.exists(fileName)

  def vFileTime(self, fileName):
    '''Returns the modification time of file `fileName` 
       or 'None' if the modification time is unavailable.'''
    return os.path.getmtime(fileName)

  def vTouch(self, fileName):
    '''Sets the current modification time for file `fileName`.'''
    os.utime(fileName, None) # equivalent: touch

  def vGetFileContents(self, fileName, logLevel = LogLevel.DEBUG):
    '''Returns contents of the file `fileName`.'''
    self.Log(Dict.msgDownloadingFile % fileName, level = logLevel)
    f = open(fileName, 'rb')
    try:
      rc = f.read()
    finally:
      f.close()
    return rc

  def vPutFileLike(self, f, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSavingFile % fileName, level = logLevel)
    lf = open(fileName, 'wb')
    try:
      for chunk in iter(lambda: f.read(32768), b''):
        lf.write(chunk)
    finally:
      lf.close()
    return OS.FileHash(fileName, hashlib.sha1())

  def vPutFile(self, fFileName, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSavingFile % fileName, level = logLevel)
    self.vMakeDirs(os.path.dirname(fileName))
    OS.CopyFile(fFileName, fileName, force = True)
    return OS.FileHash(fileName, hashlib.sha1())

  def vPutFileContents(self, contents, fileName, logLevel = LogLevel.DEBUG):
    self.Log(Dict.msgSavingFile % fileName, level = logLevel)
    f = open(fileName, 'wb')
    try:
      f.write(contents)
    finally:
      f.close()

  def PrepareMarkerFileName(self, fileName):
    '''TODO: description'''
    dirName = os.path.join(os.path.dirname(fileName), self._AttaDataExt())
    return os.path.join(dirName, os.path.basename(fileName) + self._AttaDataExt())

  def GetFileMarker(self, fileName):
    '''TODO: description'''
    try:
      markerFileName = self.PrepareMarkerFileName(fileName)
      contents = self.vGetFileContents(markerFileName)
      contents = contents.split('\n')
      timestamp, sha1 = (None, None)
      if len(contents) > 0:
        timestamp = contents[0]
      if len(contents) > 1:
        sha1 = contents[1]
    except Exception as E:
      self.Log("Error '%s' while processing the file: %s" % (str(E), markerFileName), level = LogLevel.ERROR)
      return (None, None)
    else:
      return (timestamp, sha1)

  def PutMarkerFile(self, fileName, fileSha1, packageId):
    '''TODO: description'''
    markerFileName = self.PrepareMarkerFileName(fileName)
    dirName = os.path.dirname(markerFileName)
    if not self.vFileExists(dirName):
      self.vMakeDirs(dirName)
    self.vPutFileContents(str(packageId.timestamp) + '\n' + str(fileSha1), markerFileName)

  def PrepareInfoFileName(self, fileName):
    '''TODO: description'''
    return OS.Path.RemoveExt(self.PrepareMarkerFileName(fileName)) + self._InfoExt()

  def GetInfoFile(self, fileName):
    infoFileName = self.PrepareInfoFileName(fileName)
    if self.vFileExists(infoFileName):
      return self.vGetFileContents(infoFileName)
    return None

  def GetFilesListFromInfoFile(self, infoFile):
    return infoFile.split('\n')

  def PutInfoFile(self, fileName, storedFileNames):
    self.vPutFileContents('\n'.join(storedFileNames), self.PrepareInfoFileName(fileName))

  def GetPOMFileContents(self, packageId, **tparams):
    from . import Maven
    packageId = PackageId.FromPackageId(packageId, type = Dict.pom)
    pom = Maven.Repository.GetPOMFromCache(packageId, self.Log)
    if pom != None:
      return pom

    fileName = self.PrepareFileName(packageId, self._RootDir())
    if not self.vFileExists(fileName):
      return None

    pom = self.vGetFileContents(fileName)
    Maven.Repository.PutPOMIntoCache(packageId, pom, self.Log)
    return pom

  def vPrepareFileName(self, fileName):
    '''TODO: description'''
    return os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), fileName))

  def PrepareFileName(self, packageId, rootDir = None):
    '''TODO: description'''
    if rootDir is None:
      fileName = os.path.join('.repository', self._styleImpl.GetObject().FullFileName(packageId))
      return self.vPrepareFileName(fileName)
    else:
      return os.path.join(rootDir, self._styleImpl.GetObject().FullFileName(packageId))

  def GetAll(self, fileName):
    infoFile = self.GetInfoFile(fileName)
    if infoFile is not None:
      result = self.GetFilesListFromInfoFile(infoFile)
      for i in range(len(result)):
        result[i] = os.path.join(os.path.dirname(fileName), result[i])
    else:
      result = [fileName]
    return result

  def _Get(self, packageId, scope, store, resolvedPackages):
    '''TODO: description'''
    '''returns: list of filesNames'''
    # Get the dependencies.
    additionalFiles = []
    packages = self.GetDependencies(packageId, scope)
    if packages != None:
      for p in packages:
        if not packageId.Excludes(p):
          if p not in resolvedPackages:
            resolvedPackages.append(p)
            additionalFiles += self._Get(p, scope, store, resolvedPackages)

    # Check and prepare artifact files.
    fileName = self.PrepareFileName(packageId, self._RootDir())
    if not self.vFileExists(fileName):
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))

    dirName = os.path.dirname(fileName)
    result = self.GetAll(fileName)

    if store is not None:
      # Put artifact files into store.
      packageId.timestamp, sha1 = self.GetFileMarker(fileName)
      store.SetOptionalAllowed(self.OptionalAllowed())
      filesInStore = store.Check(packageId, scope)
      if filesInStore is None:
        self.Log(Dict.msgSendingXToY % (packageId.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
        store.Put(result, dirName, packageId)
      else:
        if fileName in filesInStore:
          self.Log("Unable to store: %s in the same repository, from which it is pulled." % str(packageId), level = LogLevel.WARNING)

    result += additionalFiles
    result = RemoveDuplicates(result)

    self.Log(Dict.msgReturns % OS.Path.FromList(result), level = LogLevel.DEBUG)
    return result

  def Get(self, packageId, scope, store = None):
    return self._Get(packageId, scope, store, [])

  def GetDependencies(self, packageId, scope):
    # TODO: zrobic to jakims uniwersalnym mechanizmem, ktory pozwoli
    # rejestrowac rozne rodzaje plikow z zaleznosciami pakietow
    from . import Maven
    return Maven.Repository.GetDependenciesFromPOM(packageId,
                                                   self.GetPOMFileContents,
                                                   Dict.Scopes.map2POM.get(scope, []),
                                                   self.OptionalAllowed(),
                                                   logFn = self.Log)

  # TODO: uzyc wzorca Strategy do implementacji Check
  def _Check(self, packageId, scope, checkedPackages):
    '''returns: None or list of filesNames'''
    self.Log(Dict.msgCheckingWithX.format(str(packageId), packageId.timestamp), level = LogLevel.VERBOSE)

    fileName = self.PrepareFileName(packageId, self._RootDir())
    if not self.vFileExists(fileName):
      return None

    storedTimestamp, storedSha1 = self.GetFileMarker(fileName)
    if storedTimestamp is None:
      return None

    # If the given timestamp isn't equal to the local file timestamp 
    # (stored with the file: see Put method) then return None. 
    if packageId.timestamp is not None:
      if str(packageId.timestamp) != str(storedTimestamp):
        return None
      else:
        self.vTouch(fileName)

    # If the local file was stored earlier (modification time) 
    # than _LifeTime then return None.
    def _LifeTime():
      return timedelta(days = 14)
      #return timedelta(seconds = 5)
    fileTime = self.vFileTime(fileName)
    if fileTime is not None:
      fileTime = datetime.fromtimestamp(self.vFileTime(fileName))
      if datetime.now() - fileTime > _LifeTime():
        return None

    # Check dependencies.
    additionalFiles = []
    packages = self.GetDependencies(packageId, scope)
    if packages != None:
      for p in packages:
        if not packageId.Excludes(p):
          if p not in checkedPackages:
            checkedPackages.append(p)
            pfiles = self._Check(p, scope, checkedPackages)
            if self.OptionalAllowed() or not p.IsOptional():
              if pfiles is None:
                return None
            if pfiles: additionalFiles += pfiles

    return additionalFiles + self.GetAll(fileName)

  def Check(self, packageId, scope):
    return self._Check(packageId, scope, [])

  def Put(self, f, fBaseDirName, packageId):
    '''returns: list of filesNames'''
    self.Log('Takes: %s' % packageId.AsStrWithoutType(), level = LogLevel.INFO)

    fileName = self.PrepareFileName(packageId, self._RootDir())
    dirName = os.path.normpath(os.path.dirname(fileName))
    self.vMakeDirs(dirName)

    self.Log('to:\n  %s' % dirName, level = LogLevel.DEBUG)

    if 'read' in dir(f):
      sha1 = self.vPutFileLike(f, fileName)
      self.PutMarkerFile(fileName, sha1, packageId)
      return [fileName]
    else:
      rnames = []
      lnames = []
      for fFileName in OS.Path.AsList(f):
        if isinstance(fFileName, NamedFileLike):
          rFileName = os.path.join(dirName, os.path.relpath(fFileName.fileName, fBaseDirName))
          sha1 = self.vPutFileLike(fFileName.f, rFileName)
        else:
          rFileName = os.path.join(dirName, os.path.relpath(fFileName, fBaseDirName))
          if fFileName == rFileName:
            rFileName = os.path.join(dirName, os.path.basename(fFileName))
          sha1 = self.vPutFile(fFileName, rFileName)

        self.PutMarkerFile(rFileName, sha1, packageId)

        rnames.append(rFileName)
        lnames.append(os.path.relpath(rFileName, dirName))

      if len(lnames) > 1:
        self.PutInfoFile(fileName, lnames)

      return rnames

  def _Name(self):
    name = Task._Name(self)
    return 'Local.' + name

  def _RootDir(self):
    rootDir = None
    if self.data is not None:
      rootDir = self.data.get(Dict.rootDir, None)
    return rootDir

  def _AttaDataExt(self):
    return '.atta'

  def _InfoExt(self):
    return '.info'

