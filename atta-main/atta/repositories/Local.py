""".. Local: TODO"""
import os
import hashlib
from datetime import datetime, timedelta

from ..tools.Misc import RemoveDuplicates, NamedFileLike
from .. import Dict, LogLevel, OS, Task, PackageId
from . import ArtifactNotFoundError, Base

class Repository(Base.Repository, Task):
  """TODO: description"""
  def __init__(self, **tparams):
    Base.Repository.__init__(self, **tparams)

    self.rootDirName = self.data.get(Dict.rootDirName, None)
    if self.rootDirName:
      self.rootDirName = self.rootDirName.replace('~', os.path.expanduser('~'))

    self.useFileHashInCheck = self.data.get(Dict.useFileHashInCheck, True)
    self.lifeTime = self.data.get(Dict.lifeTime, None)
    if self.lifeTime:
      self.lifeTime = timedelta(seconds = self.lifeTime)

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

  def FileHash(self, fileName):
    return OS.FileHash(fileName, hashlib.sha1())

  def Touch(self, fileName):
    """Sets the current modification time for file *fileName*."""
    os.utime(fileName, None) # equivalent: touch

  def GetFileContents(self, fileName, logLevel = LogLevel.DEBUG):
    """Returns contents of the file *fileName*."""
    self.Log(Dict.msgReadingFile % fileName, level = logLevel)
    f = open(fileName, 'rb')
    try:
      rc = f.read()
    finally:
      f.close()
    return rc

  def PutFileLike(self, f, fileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSaving % fileName, level = logLevel)
    self.MakeDirs(os.path.dirname(fileName))
    lf = open(fileName, 'wb')
    # TODO: optimize, hash can be determined during read/write
    try:
      for chunk in iter(lambda: f.read(32768), b''):
        lf.write(chunk)
    finally:
      lf.close()
    return self.FileHash(fileName)

  def PutFile(self, srcFileName, destFileName, logLevel = LogLevel.VERBOSE):
    self.Log(Dict.msgSaving % destFileName, level = logLevel)
    self.MakeDirs(os.path.dirname(destFileName))
    # TODO: optimize, hash can be determined during copy
    OS.CopyFile(srcFileName, destFileName, force = True)
    return self.FileHash(destFileName)

  def PutFileContents(self, contents, fileName, logLevel = LogLevel.DEBUG):
    self.Log(Dict.msgSaving % fileName, level = logLevel)
    f = open(fileName, 'wb')
    try:
      f.write(contents)
    finally:
      f.close()

  def PrepareMarkerFileName(self, fileName):
    """TODO: description"""
    dirName = os.path.join(os.path.dirname(fileName), Dict.attaExt)
    return os.path.join(dirName, os.path.basename(fileName) + Dict.attaExt)

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
    return OS.Path.RemoveExt(self.PrepareMarkerFileName(fileName)) + Dict.infoExt

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

  def Url(self):
    return ''

  def CompleteFileName(self, fileName):
    """TODO: description"""
    return os.path.normpath(os.path.join(os.path.expanduser('~'), Dict.attaExt, fileName))

  def PrepareFileName(self, package):
    """TODO: description"""
    if self.rootDirName is None:
      fileName = os.path.join(Dict.repository, self._styleImpl.GetObject().FullFileName(package))
      return self.CompleteFileName(fileName)
    else:
      return os.path.join(self.rootDirName, self._styleImpl.GetObject().FullFileName(package))

  def GetAll(self, package):
    fileName = self.PrepareFileName(package)
    dirName = os.path.dirname(fileName)
    result = []
    if not package.fileNames:
      infoFile = self.GetInfoFileContents(package)
      if infoFile is not None:
        result = infoFile.split('\n')
        result = [self.NormPath(os.path.join(dirName, fn.strip())) for fn in result if fn.strip()]
      else:
        result = [self.NormPath(fileName)]
    else:
      result = [self.NormPath(os.path.join(dirName, fn)) for fn in package.fileNames]
    return result

  def CheckAndPrepareFilesForGet(self, package):
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
    allFiles = []
    problem = False
    try:
      allFiles, baseDirName = self.CheckAndPrepareFilesForGet(package)
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
        #print '***1', fileName
        return None

      storedStamp, storedSha1 = self.GetFileMarker(fileName)
      if storedStamp is None:
        #print '***2'
        return None

      if package.stamp is not None:
        if str(package.stamp) != str(storedStamp):
          #print '***3', fileName, storedStamp, package.stamp
          return None
        else:
          self.Touch(fileName)

      if self.lifeTime:
        # If the local file was stored earlier (modification time)
        # than `lifeTime` then return None.
        fileTime = self.FileTime(fileName)
        if fileTime is not None:
          fileTime = datetime.fromtimestamp(fileTime)
          if datetime.now() - fileTime > self.lifeTime:
            #print '***4', fileName
            return None

      if self.useFileHashInCheck:
        sha1 = self.FileHash(fileName)
        if sha1:
          if sha1 != storedSha1:
            #print '***5'
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
              #print '***6'
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

    self.Log('to: %s%s' % (self.Url(), self.NormPath(dirName)), level = LogLevel.DEBUG)

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
