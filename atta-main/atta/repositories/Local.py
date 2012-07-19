""".. Local: TODO"""
import os
import hashlib
from datetime import datetime, timedelta

from ..tools.Misc import RemoveDuplicates, NamedFileLike
from .. import Dict, LogLevel, OS, Task, PackageId
from .Base import ARepository
from . import ArtifactNotFoundError

def GetPOMFileContents(package):
  pass

class Repository(ARepository, Task):
  """TODO: description"""

  def NormPath(self, path):
    return os.path.normpath(path)

  def MakeDirs(self, dirName):
    OS.MakeDirs(dirName)

  def FileExists(self, fileName):
    return os.path.exists(fileName)

  def FileTime(self, fileName):
    """Returns the modification time of file *fileName*
       or `None` if the modification time is unavailable."""
    return OS.FileTimestamp(fileName)

  def Touch(self, fileName):
    """Sets the current modification time for file *fileName*."""
    os.utime(fileName, None) # equivalent: touch

  def GetFileLike(self, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgDownloadingFile % fileName, level = logLevel)
    return open(fileName, 'rb')

  def GetFileContents(self, fileName, logLevel = LogLevel.DEBUG):
    """Returns contents of the file *fileName*."""
    f = self.GetFileLike(fileName, logLevel)
    try:
      rc = f.read()
    finally:
      f.close()
    return rc

  def PutFileLike(self, f, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSavingFile % fileName, level = logLevel)
    self.MakeDirs(os.path.dirname(fileName))
    lf = open(fileName, 'wb')
    try:
      for chunk in iter(lambda: f.read(32768), b''):
        lf.write(chunk)
    finally:
      lf.close()
    return OS.FileHash(fileName, hashlib.sha1())

  def PutFile(self, srcFileName, destFileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSavingFile % destFileName, level = logLevel)
    self.MakeDirs(os.path.dirname(destFileName))
    OS.CopyFile(srcFileName, destFileName, force = True)
    return OS.FileHash(destFileName, hashlib.sha1())

  def PutFileContents(self, contents, fileName, logLevel = LogLevel.DEBUG):
    self.Log(Dict.msgSavingFile % fileName, level = logLevel)
    f = open(fileName, 'wb')
    try:
      f.write(contents)
    finally:
      f.close()

  def PrepareMarkerFileName(self, fileName):
    """TODO: description"""
    dirName = os.path.join(os.path.dirname(fileName), self._AttaDataExt())
    return os.path.join(dirName, os.path.basename(fileName) + self._AttaDataExt())

  def GetFileMarker(self, fileName):
    """TODO: description"""
    markerFileName = self.PrepareMarkerFileName(fileName)
    try:
      if not self.FileExists(markerFileName):
        return None, None
      contents = self.GetFileContents(markerFileName)
      contents = contents.split('\n')
      stamp, sha1 = (None, None)
      if len(contents) > 0:
        stamp = contents[0]
      if len(contents) > 1:
        sha1 = contents[1]
    except Exception as E:
      self.Log("Error '%s' while processing the file: %s" % (str(E), markerFileName), level = LogLevel.ERROR)
      return None, None
    else:
      return stamp, sha1

  def PutMarkerFile(self, fileName, fileSha1, package):
    """TODO: description"""
    markerFileName = self.PrepareMarkerFileName(fileName)
    dirName = os.path.dirname(markerFileName)
    if not self.FileExists(dirName):
      self.MakeDirs(dirName)
    self.PutFileContents(str(package.stamp) + '\n' + str(fileSha1), markerFileName)

  def PrepareInfoFileName(self, package):
    """TODO: description"""
    fileName = self.PrepareFileName(package)
    return OS.Path.RemoveExt(self.PrepareMarkerFileName(fileName)) + self._InfoExt()

  def GetInfoFileContents(self, package):
    infoFileName = self.PrepareInfoFileName(package)
    if self.FileExists(infoFileName):
      return self.GetFileContents(infoFileName)
    return None

  def PutInfoFile(self, package, storedFileNames):
    self.PutFileContents('\n'.join(storedFileNames), self.PrepareInfoFileName(package))

  def GetPOMFileContents(self, package, **tparams):
    from . import Maven
    package = PackageId.FromPackage(package, type = Dict.pom)
    pom = Maven.Repository.GetPOMFromCache(package, self.Log)
    if pom:
      return pom

    fileName = self.PrepareFileName(package)
    if not self.FileExists(fileName):
      return None

    pom = self.GetFileContents(fileName)
    Maven.Repository.PutPOMIntoCache(package, pom, self.Log)
    return pom

  def CompleteFileName(self, fileName):
    """TODO: description"""
    return os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), fileName))

  def PrepareFileName(self, package):
    """TODO: description"""
    rootDirName = self._RootDirName()
    if rootDirName is None:
      fileName = os.path.join(Dict.repository, self._styleImpl.GetObject().FullFileName(package))
      return self.CompleteFileName(fileName)
    else:
      return os.path.join(rootDirName, self._styleImpl.GetObject().FullFileName(package))

  def GetAll(self, package):
    fileName = self.PrepareFileName(package)
    dirName = os.path.dirname(fileName)
    result = []
    if not package.fileNames:
      infoFile = self.GetInfoFileContents(package)
      if infoFile is not None:
        result = infoFile.split('\n')
      else:
        result = [fileName]
    else:
      result = package.fileNames
    result = [self.NormPath(os.path.join(dirName, fn.strip())) for fn in result if fn.strip()]
    return result

  def _CheckAndPrepareFilesForGet(self, package):
    """Check and prepare the artifact files and get the artifact stamp if available."""
    fileName = self.PrepareFileName(package)
    dirName = os.path.dirname(fileName)
    allFiles = self.GetAll(package)
    for fn in allFiles:
      if not self.FileExists(fn):
        raise IOError(Dict.errFileNotExists % fn)
    if allFiles:
      package.stamp, _ = self.GetFileMarker(allFiles[0])
    return allFiles, dirName

  def _Get(self, package, scope, store, resolvedPackages):
    """TODO: description"""
    '''returns: list of filesNames'''
    # Get the dependencies.
    additionalFiles = []
    for p in self.GetDependencies(package, scope) or ():
      if not package.Excludes(p):
        if p not in resolvedPackages:
          resolvedPackages.append(p)
          additionalFiles += self._Get(p, scope, store, resolvedPackages)

    # Get the artifact files.
    problem = False
    try:
      allFiles, baseDirName = self._CheckAndPrepareFilesForGet(package)
    except Exception as E:
      self.Log(str(E), level = LogLevel.ERROR)
      problem = True
    else:
      # Put the artifact files into store if specified.
      if store is not None:
        if self.PrepareFileName(package) == store.PrepareFileName(package):
          self.Log("Unable to store: %s in the same repository from which it is pulled." % str(package), level = LogLevel.WARNING)
        else:
          filesInStore = store.Check(package, scope)
          if filesInStore is None:
            self.Log(Dict.msgSendingXToY % (package.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
            try:
              store.Put(baseDirName, allFiles, package)
            except Exception as E:
              self.Log(Dict.errXWhileSavingY % (str(E), str(package)), level = LogLevel.ERROR)
              problem = True

    if problem:
      if not package.optional:
        raise ArtifactNotFoundError(self, Dict.errFailedToAssembleX % str(package))
      else:
        allFiles = []
        additionalFiles = []

    # Return all found files.
    allFiles += additionalFiles
    allFiles = RemoveDuplicates(allFiles)
    self.Log(Dict.msgReturns % OS.Path.FromList(allFiles), level = LogLevel.DEBUG)
    return allFiles

  def Get(self, package, scope, store = None):
    if store:
      store.SetOptionalAllowed(self.OptionalAllowed())
    return self._Get(package, scope, store, [])

  def GetDependencies(self, package, scope):
    # TODO: zrobic to jakims uniwersalnym mechanizmem, ktory pozwoli
    # rejestrowac rozne rodzaje plikow z zaleznosciami pakietow

    #fileName = self.PrepareFileName(package)
    allFiles = self.GetAll(package)

    packageHasPOMFile =  Dict.pom in [OS.Path.Ext(fileName).lower() for fileName in allFiles]
    if packageHasPOMFile:
      from . import Maven
      return Maven.Repository.GetDependenciesFromPOM(package,
                                                     self.GetPOMFileContents,
                                                     Dict.Scopes.map2POM.get(scope, []),
                                                     self.OptionalAllowed(),
                                                     logFn = self.Log)

  # TODO: uzyc wzorca Strategy do implementacji Check
  def _Check(self, package, scope, checkedPackages):
    """returns: None or list of filesNames"""
    self.Log(Dict.msgCheckingWithX.format(str(package), package.stamp), level = LogLevel.VERBOSE)

    allFiles = self.GetAll(package)
    for fileName in allFiles:
      if not self.FileExists(fileName):
        return None

      storedStamp, storedSha1 = self.GetFileMarker(fileName)
      if storedStamp is None:
        return None

      # If the given stamp isn't equal to the local file stamp
      # (stored with the file: see Put method) then return None.
      if package.stamp is not None:
        if str(package.stamp) != str(storedStamp):
          return None
        else:
          self.Touch(fileName)

      # If the local file was stored earlier (modification time)
      # than _LifeTime then return None.
      def _LifeTime():
        return timedelta(seconds = self.data.get('lifeTime', 3600 * 24 * 14)) # 14 days
      fileTime = self.FileTime(fileName)
      if fileTime is not None:
        fileTime = datetime.fromtimestamp(fileTime)
        if datetime.now() - fileTime > _LifeTime():
          return None

    # Check dependencies.
    additionalFiles = []
    for p in self.GetDependencies(package, scope) or ():
      if not package.Excludes(p):
        if p not in checkedPackages:
          checkedPackages.append(p)
          pfiles = self._Check(p, scope, checkedPackages)
          if self.OptionalAllowed() or not p.optional:
            if pfiles is None:
              return None
          if pfiles: additionalFiles += pfiles

    return allFiles + additionalFiles

  def Check(self, package, scope):
    return self._Check(package, scope, [])

  def Put(self, fBaseDirName, files, package):
    """returns: list of filesNames"""
    self.Log('Takes: %s' % package.AsStrWithoutType(), level = LogLevel.INFO)

    fileName = self.PrepareFileName(package)
    dirName = os.path.normpath(os.path.dirname(fileName))
    self.MakeDirs(dirName)

    self.Log('to: %s' % dirName, level = LogLevel.DEBUG)

    if 'read' in dir(files):
      sha1 = self.PutFileLike(files, fileName)
      self.PutMarkerFile(fileName, sha1, package)
      return [fileName]

    else:
      rnames = []
      lnames = []
      for fFileName in OS.Path.AsList(files):
        if isinstance(fFileName, NamedFileLike):
          rFileName = os.path.join(dirName, os.path.relpath(fFileName.fileName, fBaseDirName))
          sha1 = self.PutFileLike(fFileName.f, rFileName)
        else:
          rFileName = os.path.join(dirName, os.path.relpath(fFileName, fBaseDirName))
          if fFileName == rFileName:
            rFileName = os.path.join(dirName, os.path.basename(fFileName))
          sha1 = self.PutFile(fFileName, rFileName)

        self.PutMarkerFile(rFileName, sha1, package)

        rnames.append(rFileName)
        lnames.append(os.path.relpath(rFileName, dirName))

      if len(lnames) > 1:
        self.PutInfoFile(package, lnames)

      return rnames

  def _Name(self):
#    name = Task._Name(self)
#    return 'Local.' + name
    return 'Local'

  def _RootDirName(self):
    rootDirName = None
    if self.data is not None:
      rootDirName = self.data.get(Dict.rootDirName, None)
      if rootDirName:
        rootDirName = rootDirName.replace('~', os.path.expanduser('~'))
    return rootDirName

  def _AttaDataExt(self):
    return '.atta'

  def _InfoExt(self):
    return '.info'
