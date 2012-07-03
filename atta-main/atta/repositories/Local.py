'''.. Local: TODO'''
import os
import hashlib
from datetime import datetime, timedelta

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import NamedFileLike, LogLevel
from Base import ARepository
from . import ArtifactNotFoundError
import atta.Dict as Dict
import Maven

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
    
  def vPutFileLike(self, f, fileName):
    with open(fileName, 'wb') as lf:
      for chunk in iter(lambda: f.read(32768), b''): 
        lf.write(chunk)
    return OS.FileHash(fileName, hashlib.sha1())
  
  def vPutFile(self, fFileName, fileName):
    self.vMakeDirs(os.path.dirname(fileName))
    OS.CopyFile(fFileName, fileName, force = True)
    return OS.FileHash(fileName, hashlib.sha1())
    
  def PrepareMarkerFileName(self, fileName):
    '''TODO: description'''
    dirName = os.path.join(os.path.dirname(fileName), self._AttaDataExt())
    return os.path.join(dirName, os.path.basename(fileName) + self._AttaDataExt())
  
  def vGetFileMarkerContents(self, markerFileName):
    with open(markerFileName, 'rb') as f:
      return f.read()
    
  def GetFileMarker(self, fileName):
    '''TODO: description'''
    try:
      markerFileName = self.PrepareMarkerFileName(fileName)
      contents = self.vGetFileMarkerContents(markerFileName)
      contents = contents.split('\n')
      timestamp, sha1 = (None, None)
      if len(contents) > 0:
        timestamp = contents[0]
      if len(contents) > 1:
        sha1 = contents[1]
    except:
      return (None, None)
    else:
      return (timestamp, sha1)
    
  def vPutMarkerFileContents(self, markerFileName, contents):
    with open(markerFileName, 'wb') as f:
      f.write(contents)
  
  def PutMarkerFile(self, fileName, fileSha1, packageId):
    '''TODO: description'''
    markerFileName = self.PrepareMarkerFileName(fileName)
    dirName = os.path.dirname(markerFileName)
    if not self.vFileExists(dirName):
      self.vMakeDirs(dirName)
    self.vPutMarkerFileContents(markerFileName, 
                                str(packageId.timestamp) + '\n' + str(fileSha1))
      
  def PrepareInfoFileName(self, fileName):
    '''TODO: description'''
    return OS.Path.RemoveExt(self.PrepareMarkerFileName(fileName)) + self._InfoExt()

  def vGetInfoFileContents(self, infoFileName):
    with open(infoFileName, 'rb') as f:
      return f.read()

  def GetInfoFile(self, fileName):  
    infoFileName = self.PrepareInfoFileName(fileName)
    if self.vFileExists(infoFileName):
      return self.vGetInfoFileContents(infoFileName)
    return None
  
  def GetFilesListFromInfoFile(self, infoFile):
    return infoFile.split('\n')
  
  def vPutInfoFileContents(self, infoFileName, contents):
    with open(infoFileName, 'wb') as f:
      f.write(contents)
      
  def PutInfoFile(self, fileName, storedFileNames):
    self.vPutInfoFileContents(self.PrepareInfoFileName(fileName), '\n'.join(storedFileNames))

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
  
  def Get(self, packageId, scope, store = None):
    '''TODO: description'''
    '''returns: list of filesNames'''
    # Get the dependencies.
    additionalFiles = []
    packages = self.GetDependenciesFromPOM(packageId, scope)
    if packages != None:
      for p in packages:
        additionalFiles += self.Get(p, scope, store)
    
    # Check and prepare artifact files.
    fileName = self.PrepareFileName(packageId, self._RootDir())
    if not self.vFileExists(fileName):
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    dirName = os.path.dirname(fileName)
    result = self.GetAll(fileName)
      
    if store is not None:
      # Put artifact files into store.
      packageId.timestamp, sha1 = self.GetFileMarker(fileName)
      filesInStore = store.Check(packageId, scope)
      if filesInStore is None:
        self.Log('Uploading: %s to: %s' %(str(packageId), store._Name()), level = LogLevel.INFO)
        store.Put(result, dirName, packageId)
      else:
        if fileName in filesInStore:
          self.Log("Unable to store: %s in the same repository, from which it is pulled." % str(packageId), level = LogLevel.WARNING)

    result += additionalFiles
    self.Log('Returns: %s' % OS.Path.FromList(result), level = LogLevel.VERBOSE)
    return result
  
  def vGetPOMFileContents(self, pomFileName):
    with open(pomFileName, 'rb') as f:
      return f.read()

  def GetDependenciesFromPOM(self, packageId, scope):
    fileName = self.PrepareFileName(packageId, self._RootDir())
    fileName = OS.Path.JoinExt(OS.Path.RemoveExt(fileName), Dict.pom)
    if not self.vFileExists(fileName):
      return None
    return Maven.Repository.GetDependenciesFromPOM(self.vGetPOMFileContents(fileName), Dict.Scopes.map2POM.get(scope, []))
  
  def _LifeTime(self):
    return timedelta(days = 14)
    #return timedelta(seconds = 5)

  # TODO: uzyc wzorca Strategy do implementacji Check
  def Check(self, packageId, scope):
    '''returns: None or list of filesNames'''
    self.Log(Dict.msgChecking.format(str(packageId)), level = LogLevel.VERBOSE)

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
    fileTime = self.vFileTime(fileName)
    if fileTime is not None:
      fileTime = datetime.fromtimestamp(self.vFileTime(fileName))
      if datetime.now() - fileTime > self._LifeTime():
        return None
    
    # Check dependencies from POM file.
    additionalFiles = []
    packages = self.GetDependenciesFromPOM(packageId, scope)
    if packages != None:
      for dPackageId in packages:
        r = self.Check(dPackageId, scope)
        if r == None:
          return None
        additionalFiles += r
        
    return additionalFiles + self.GetAll(fileName)
  
  def Put(self, f, fBaseDirName, packageId):
    '''returns: list of filesNames'''
    self.Log('Takes: %s' % str(packageId), level = LogLevel.INFO)

    fileName = self.PrepareFileName(packageId, self._RootDir())
    dirName = os.path.normpath(os.path.dirname(fileName))
    self.vMakeDirs(dirName)
    
    self.Log('to: %s' % dirName, level = LogLevel.INFO)
    
    if 'read' in dir(f):
      sha1 = self.vPutFileLike(f, fileName)
      self.PutMarkerFile(fileName, sha1, packageId)
      self.LogIterable('with files:', [os.path.relpath(fileName, dirName)], level = LogLevel.VERBOSE)
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
      
      self.LogIterable('with files:', lnames, level = LogLevel.VERBOSE)
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
  
