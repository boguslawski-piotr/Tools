'''.. Remote: TODO'''
from ftplib import FTP, error_perm
import os
import hashlib
import tempfile

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import NamedFileLike, LogLevel
from atta import AttaError
from Base import ARepository
from . import ArtifactNotFoundError
import atta.Dictionary as Dictionary
import Local

class Repository(Local.Repository):
  '''TODO: description'''
  def __init__(self, data):
    ARepository.__init__(self, data)
    
    self.host = data.get(Dictionary.host)
    if self.host == None:
      raise AttaError(self, 'Not specified: ' + Dictionary.host)
    if self._RootDir() == None:
      raise AttaError(self, 'Not specified: ' + Dictionary.rootDir)

    self.ftp = FTP()
    self.ftp.set_debuglevel(0)
    
    self.port = data.get(Dictionary.port, 21)
    self.ftp.connect(self.host, self.port)
    
    # TODO: anonymous login?
    user = data.get(Dictionary.user)
    passwd = data.get(Dictionary.pasword)
    self.ftp.login(user, passwd)
    
    self.ftp.set_pasv(data.get(Dictionary.passive, False))
    
    self.cache = None
    if data.get(Dictionary.useCache, True):
      # NOTE: Cache is on the local file system.
      # Any change of this assumption will result in the need 
      # to change the function: self.vPutFileLike(). 
      cacheDirName = os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), '.ftpcache'))
      self.cache = Local.Repository({
                                     Dictionary.style   : data.get(Dictionary.style, ARepository.GetDefaultStyleImpl()), 
                                     Dictionary.rootDir : cacheDirName
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
    except error_perm as E:
      if str(E).find('550') >= 0:
        pass
      else:
        raise
    
  def vFileSize(self, fileName):
    try:
      fileSize = self.ftp.size(OS.Path.NormUnix(fileName))
    except error_perm as E:
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
    # I don't known method for simulate touch on ftp server :(
    pass
  
  def GetFileLikeCallback(self, data):
    #self.Log('*')
    self.tempFile.write(data)
    
  def GetFileLike(self, fileName):
    #self.Log('GetFileLike ' + OS.Path.NormUnix(fileName))
    self.tempFile = tempfile.SpooledTemporaryFile()
    self.ftp.retrbinary('RETR ' + OS.Path.NormUnix(fileName), self.GetFileLikeCallback)
    self.tempFile.seek(0)
    return self.tempFile
  
  def VPutFileLikeCallback(self, data):
    #self.Log('*')
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
    
    self.sha1 = hashlib.sha1()
    self.ftp.storbinary('STOR ' + OS.Path.NormUnix(fileName), f, callback = self.VPutFileLikeCallback) #, blocksize, callback, rest
    sha1 = self.sha1.hexdigest()
    self.sha1 = None

    if self.fileInCache != None:
      try: self.fileInCache.close()
      finally: self.fileInCache = None
    
    return sha1
  
  def vPutFile(self, fFileName, fileName):
    self.vMakeDirs(os.path.dirname(fileName))
    with open(fFileName, 'rb') as f:
      return self.vPutFileLike(f, fileName)
    
  def vGetFileMarkerContents(self, markerFileName):
    with self.GetFileLike(markerFileName) as f:
      return f.read()
  
  def vPutMarkerFileContents(self, markerFileName, contents):
    #self.Log(markerFileName)
    with tempfile.SpooledTemporaryFile() as f:
      f.write(contents)
      f.seek(0)
      self.vPutFileLike(f, markerFileName)

  def vGetInfoFileContents(self, infoFileName):
    return self.vGetFileMarkerContents(infoFileName)

  def vPutInfoFileContents(self, infoFileName, contents):
    self.vPutMarkerFileContents(infoFileName, contents)

  def vPrepareFileName(self, fileName):
    return fileName

  def Get(self, packageId, scope, store = None):
    '''TODO: description'''
    '''returns: list of filesNames'''
    self._DumpParams(locals())
    if not packageId:
      raise AttaError(self, 'Not enough parameters.')

    if store is None:
      store = self.cache
    if store is None:
      raise AttaError(self, 'Not specified: ' + Dictionary.putIn)
      
    filesInStore = store.Check(packageId, scope)
    if filesInStore is None:
      self.Log('Fetching information for: ' + str(packageId), level = LogLevel.INFO)
      fileName = self.PrepareFileName(packageId, self._RootDir())
      if self.vFileExists(fileName):
        packageId.timestamp, sha1 = self.GetFileMarker(fileName)
        if packageId.timestamp is not None:
          filesInStore = store.Check(packageId, scope)
            
        if filesInStore is None:
          # Get the dependencies.
          filesInStore = []
          packages = self.GetDependenciesFromPOM(packageId, scope)
          if packages != None:
            for p in packages:
              filesInStore += self.Get(p, scope, store)
          
          # Get artifact.
          self.Log('Downloading: %s to: %s' % (packageId, store._Name()), level = LogLevel.INFO)
          filesToDownload = []
          for rFileName in self.GetAll(fileName):
            filesToDownload.append(NamedFileLike(rFileName, self.GetFileLike(rFileName)))
          dirName = os.path.dirname(fileName)
          try:
            filesInStore += store.Put(filesToDownload, dirName, packageId)
          finally:
            for i in range(len(filesToDownload)):
              filesToDownload[i] = None 
        else:
          self.Log('Up to date.', level = LogLevel.VERBOSE)
      
    if filesInStore is None or len(filesInStore) <= 0:
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    
    self.Log('Returns: %s' % OS.Path.FromList(filesInStore), level = LogLevel.VERBOSE)
    return filesInStore

  def _ChangeFileNamesToFtpUrls(self, fileNames):
    if fileNames != None:
      for i in range(len(fileNames)):
        fileNames[i] = 'ftp://' + self.host + ':' + str(self.port) + '/' + OS.Path.NormUnix(fileNames[i])
    return fileNames
    
  def vGetPOMFileContents(self, pomFileName):
    return self.vGetFileMarkerContents(pomFileName)

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
