'''.. Remote: TODO'''
from ftplib import FTP, error_perm
import os
import hashlib
import tempfile

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import NamedFileLike, LogLevel
from atta import Atta, AttaError, GetProject
from Base import ARepository
from . import ArtifactNotFoundError
import Local

class Repository(Local.Repository):
  '''TODO: description'''
  def __init__(self, data):
    ARepository.__init__(self, data)
    
    self.host = data.get(ARepository.Dictionary.host)
    if self.host == None:
      raise AttaError(self, 'Not specified: ' + ARepository.Dictionary.host)
    if self._RootDir() == None:
      raise AttaError(self, 'Not specified: ' + ARepository.Dictionary.rootDir)

    self.ftp = FTP()
    self.ftp.set_debuglevel(0)
    
    self.port = data.get(ARepository.Dictionary.port)
    self.ftp.connect(self.host, self.port)
    
    user = data.get(ARepository.Dictionary.user)
    passwd = data.get(ARepository.Dictionary.pasword)
    self.ftp.login(user, passwd)
    
    self.ftp.set_pasv(data.get(ARepository.Dictionary.passive, False))
  
  def __del__(self):
    try:
      if self.ftp != None:
        self.ftp.close()
    except:
      pass
    finally:
      self.ftp = None
      
  def VMakeDirs(self, dirName):
    try:
      self.ftp.mkd(OS.Path.NormUnix(dirName))
    except error_perm as E:
      if str(E).find('550') >= 0:
        pass
      else:
        raise
    
  def VFileExists(self, fileName):
    #self.Log('VFileExist ' + OS.Path.NormUnix(fileName))
    try:
      fileSize = self.ftp.size(OS.Path.NormUnix(fileName))
    except error_perm as E:
      if str(E).find('550') >= 0:
        return False
      else:
        raise
    return fileSize != None
  
  def VFileTime(self, fileName):
    self.Log('VFileTime')
    return None
    
  def VTouch(self, fileName):
    self.Log('VFileTime')
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
    pass
  
  def VPutFileLike(self, f, fileName):
    self.sha1 = hashlib.sha1()
    self.ftp.storbinary('STOR ' + OS.Path.NormUnix(fileName), f, callback = self.VPutFileLikeCallback) #, blocksize, callback, rest
    sha1 = self.sha1.hexdigest()
    self.sha1 = None
    #self.Log(sha1)
    return sha1
  
  def VPutFile(self, fFileName, fileName):
    self.VMakeDirs(os.path.dirname(fileName))
    with open(fFileName, 'rb') as f:
      return self.VPutFileLike(f, fileName)
    
  def VGetFileMarker(self, markerFileName):
    with self.GetFileLike(markerFileName) as f:
      contents = f.read()
      #self.Log(contents)
      return contents
  
  def VPutMarkerFile(self, markerFileName, contents):
    #self.Log(markerFileName)
    with tempfile.SpooledTemporaryFile() as f:
      f.write(contents)
      f.seek(0)
      self.VPutFileLike(f, markerFileName)

  def VGetInfoFile(self, infoFileName):
    return self.VGetFileMarker(infoFileName)

  def VPutInfoFile(self, infoFileName, contents):
    self.VPutMarkerFile(infoFileName, contents)

  def VPrepareFileName(self, fileName):
    return fileName

  def Get(self, packageId, store = None):
    '''TODO: description'''
    '''returns: list of filesNames'''
    self._DumpParams(locals())
    
    if store is None or not packageId:
      raise AttaError(self, 'Not enough parameters.')

    filesInStore = store.Check(packageId)
    if filesInStore is None:
      self.Log('Fetching information for: ' + str(packageId), level = LogLevel.INFO)
      fileName = self.PrepareFileName(packageId, self._RootDir())
      if self.VFileExists(fileName):
        packageId.timestamp, sha1 = self.GetFileMarker(fileName)
        if packageId.timestamp is not None:
          filesInStore = store.Check(packageId)
            
        if filesInStore is None:
          self.Log('Downloading: %s to: %s' % (packageId, store._Name()), level = LogLevel.INFO)
          downloadedFiles = []
          for rFileName in self.GetAll(fileName):
            downloadedFiles.append(NamedFileLike(rFileName, self.GetFileLike(rFileName)))
          dirName = os.path.dirname(fileName)
          filesInStore = store.Put(downloadedFiles, dirName, packageId)
          for i in range(len(downloadedFiles) - 1):
            downloadedFiles[i] = None 
        else:
          self.Log('Up to date.', level = LogLevel.VERBOSE)
      
    if filesInStore is None or len(filesInStore) <= 0:
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    
    self.Log('Returns: %s' % OS.Path.FromList(filesInStore), level = LogLevel.VERBOSE)
    return filesInStore

  def _Name(self):
    name = Task._Name(self)
    return 'Ftp.' + name
