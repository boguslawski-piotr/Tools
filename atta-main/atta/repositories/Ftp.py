'''.. Remote: TODO'''
import ftplib
import os
import hashlib
import tempfile
from time import sleep

from ..tasks.Base import Task
from ..tools.Misc import RemoveDuplicates, NamedFileLike, LogLevel
from ..tools import OS
from .. import AttaError
from .. import Dict
from .Base import ARepository
from . import ArtifactNotFoundError
from . import Local

class Repository(Local.Repository):
  '''TODO: description'''
  def __init__(self, data):
    ARepository.__init__(self, data)
    
    self.host = data.get(Dict.host)
    if self.host == None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.host))
    if self._RootDir() == None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.rootDir))

    self.ftp = ftplib.FTP()
    self.ftp.set_debuglevel(0)
    
    self.port = data.get(Dict.port, 21)
    self.ftp.connect(self.host, self.port)
    
    # TODO: anonymous login?
    user = data.get(Dict.user)
    passwd = data.get(Dict.pasword)
    self.ftp.login(user, passwd)
    
    self.ftp.set_pasv(data.get(Dict.passive, False))
    
    self.cache = None
    if data.get(Dict.useCache, True):
      # NOTE: Cache is on the local file system.
      # Any change of this assumption will result in the need 
      # to change the function: self.vPutFileLike(). 
      cacheDirName = os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), '.ftpcache'))
      self.cache = Local.Repository({
                                     Dict.style   : data.get(Dict.style, ARepository.GetDefaultStyleImpl()), 
                                     Dict.rootDir : cacheDirName
                                    })
  
  def __del__(self):
    try:
      if self.ftp != None:
        self.ftp.close()
    except:
      pass
    finally:
      self.ftp = None
      
  def vMakeDirs(self, dirName):
    try:
      self.ftp.mkd(OS.Path.NormUnix(dirName))
    except ftplib.error_perm as E:
      if str(E).find('550') >= 0:
        pass
      else:
        raise
    
  def vFileSize(self, fileName):
    try:
      fileSize = self.ftp.size(OS.Path.NormUnix(fileName))
    except ftplib.error_perm as E:
      if str(E).find('550') >= 0:
        return OS.INVALID_FILE_SIZE
      else:
        raise
    return fileSize if fileSize != None else OS.INVALID_FILE_SIZE
  
  def vFileExists(self, fileName):
    return self.vFileSize(fileName) != OS.INVALID_FILE_SIZE
  
  def vFileTime(self, fileName):
    # TODO: implement?
    return None
    
  def vTouch(self, fileName):
    # TODO: I don't known method for simulate touch on ftp server :(
    pass
  
  def GetFileLikeCallback(self, data):
    self.tempFile.write(data)
    
  def GetFileLike(self, fileName):
    self.tempFile = tempfile.SpooledTemporaryFile()
    fileName = OS.Path.NormUnix(fileName)
    self.Log(Dict.msgDownloadingFile % fileName, level = LogLevel.VERBOSE)
  
    maxRetries = self.data.get(Dict.maxRetries, 3)
    retries = 0
    while retries < maxRetries:
      try:
        self.ftp.retrbinary('RETR ' + fileName, self.GetFileLikeCallback)
        break
      except ftplib.Error as E:
        self.Log("Error '%s' while downloading file: %s" % (str(E), fileName), level = LogLevel.WARNING)
        self.Log('Retry download (%d).' % (retries + 1), level = LogLevel.WARNING)
        self.tempFile.seek(0)
        retries += 1
        if retries >= maxRetries:
          raise
        sleep(1.00)
        
    self.tempFile.seek(0)
    return self.tempFile
  
  def _vPutFileLikeCallback(self, data):
    self.sha1.update(data)
    if self.fileInCache != None:
      self.fileInCache.write(data)
  
  def vPutFileLike(self, f, fileName):
    self.fileInCache = None
    if self.cache != None:
      # NOTE: We assume that the cache is a repository on the file system.
      # See also the notes in self.__init__().
      fileNameInCache = os.path.join(self.cache._RootDir(), os.path.relpath(fileName, self._RootDir()))
      OS.MakeDirs(os.path.dirname(fileNameInCache))
      self.fileInCache = open(fileNameInCache, 'wb')
    
    fileName = OS.Path.NormUnix(fileName)
    self.Log(Dict.msgSavingFile % fileName, level = LogLevel.VERBOSE)

    startPos = 0
    if 'tell' in dir(f):
      startPos = f.tell()
      
    maxRetries = self.data.get(Dict.maxRetries, 3)
    retries = 0
    while retries < maxRetries:
      try:
        self.sha1 = hashlib.sha1()
        self.ftp.storbinary('STOR ' + fileName, f, callback = self._vPutFileLikeCallback) #, blocksize, callback, rest
        break
      except ftplib.Error as E:
        self.Log("Error '%s' while sending file: %s" % (str(E), fileName), level = LogLevel.WARNING)
        self.Log('Retry sending (%d).' % (retries + 1), level = LogLevel.WARNING)
        f.seek(startPos) 
        if self.fileInCache != None:
          self.fileInCache.seek(0)
        retries += 1
        if retries >= maxRetries:
          raise
        sleep(1.00)
        
    sha1 = self.sha1.hexdigest()
    self.sha1 = None

    if self.fileInCache != None:
      try: self.fileInCache.close()
      finally: self.fileInCache = None
    
    return sha1
  
  def vPutFile(self, fFileName, fileName):
    self.vMakeDirs(os.path.dirname(fileName))
    f = open(fFileName, 'rb')
    try:
      rc = self.vPutFileLike(f, fileName)
    finally:
      f.close()
    return rc
  
  def vGetMarkerFileContents(self, markerFileName):
    if self.cache != None:
      # NOTE: We assume that the cache is a repository on the file system.
      # See also the notes in self.__init__().
      markerFileNameInCache = os.path.join(self.cache._RootDir(), os.path.relpath(markerFileName, self._RootDir()))
      try:
        return self.cache.vGetMarkerFileContents(markerFileNameInCache)
      except: 
        pass
      
    f = self.GetFileLike(markerFileName)
    try:  
      rc = f.read()
    finally:
      f.close()
    return rc
  
  def vPutMarkerFileContents(self, markerFileName, contents):
    f = tempfile.SpooledTemporaryFile()
    f.write(contents)
    f.seek(0)
    self.vPutFileLike(f, markerFileName)

  def vGetInfoFileContents(self, infoFileName):
    return self.vGetMarkerFileContents(infoFileName)

  def vPutInfoFileContents(self, infoFileName, contents):
    self.vPutMarkerFileContents(infoFileName, contents)

  def vPrepareFileName(self, fileName):
    return fileName

  def _Get(self, packageId, scope, store, resolvedPackages):
    '''TODO: description'''
    '''returns: list of filesNames'''
    self._DumpParams(locals())
    if not packageId:
      raise AttaError(self, 'Not enough parameters.')

    if store is None:
      store = self.cache
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))
    store.SetOptionalAllowed(self.OptionalAllowed())

    filesInStore = store.Check(packageId, scope)
    if filesInStore is None:
      fileName = self.PrepareFileName(packageId, self._RootDir())
      if self.vFileExists(fileName):
        packageId.timestamp, sha1 = self.GetFileMarker(fileName)
        if packageId.timestamp is not None:
          filesInStore = store.Check(packageId, scope)
        if filesInStore is None:
          download = True
          filesInStore = []
          
          # Get the dependencies.
          packages = self.GetDependenciesFromPOM(packageId, scope)
          if packages != None:
            for p in packages:
              if not packageId.Excludes(p):
                if p not in resolvedPackages:
                  resolvedPackages.append(p)
                  filesInStore += self._Get(p, scope, store, resolvedPackages)
          
          # Get artifact.
          if download:
            self.Log(Dict.msgDownloading % str(packageId), level = LogLevel.INFO)
            filesToDownload = []
            try:
              for rFileName in self.GetAll(fileName):
                filesToDownload.append(NamedFileLike(rFileName, self.GetFileLike(rFileName)))
              filesInStore += store.Put(filesToDownload, os.path.dirname(fileName), packageId)
            finally:
              for i in range(len(filesToDownload)):
                filesToDownload[i] = None 
      
    if filesInStore is None or len(filesInStore) <= 0:
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    
    filesInStore = RemoveDuplicates(filesInStore)
    self.Log(Dict.msgReturns % OS.Path.FromList(filesInStore), level = LogLevel.DEBUG)
    return filesInStore
  
  def Get(self, packageId, scope, store = None):
    self._Get(packageId, scope, store, [])
    
  def _ChangeFileNamesToFtpUrls(self, fileNames):
    if fileNames != None:
      for i in range(len(fileNames)):
        fileNames[i] = 'ftp://' + self.host + ':' + str(self.port) + '/' + OS.Path.NormUnix(fileNames[i])
    return fileNames
    
  def vGetPOMFileContents(self, pomFileName):
    return self.vGetMarkerFileContents(pomFileName)

  def Check(self, packageId, scope):
    cresult = None
    if self.cache != None:
      # First checks the local cache and if it does not have 
      # the correct files then forces a full refresh.
      cresult = self.cache.Check(packageId, scope)
      if cresult == None:
        return None
    # Then check the files on ftp.
    result = Local.Repository.Check(self, packageId, scope)
    if result == None:
      return None
    # Usually we give the file names from the local cache.
    # But in the case when the repository is set to not use cache we give the full urls.
    return cresult if cresult != None else self._ChangeFileNamesToFtpUrls(result)
  
  def Put(self, f, fBaseDirName, packageId):
    # Put the files on ftp at the same time (if the repository use cache) 
    # creating an exact copy in the local cache (see also: vPutFileLike method). 
    result = Local.Repository.Put(self, f, fBaseDirName, packageId)
    if result != None and self.cache != None:
      # Because the cache had just been updated, we give local file names.
      for i in range(len(result)):
        result[i] = os.path.join(self.cache._RootDir(), os.path.relpath(result[i], self._RootDir()))
      return result
    # If the repository is set to not use cache we give the full urls.
    return self._ChangeFileNamesToFtpUrls(result)
  
  def _Name(self):
    name = Task._Name(self)
    return 'Ftp.' + name
