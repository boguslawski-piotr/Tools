import os
import shutil
import hashlib
from datetime import datetime, timedelta

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..loggers import Compact
from ..Interfaces import IRepository
from atta import AttaError

class Repository(IRepository, Task):
  '''TODO: description'''

  def PrepareRealFileName(self, fileName):
    '''TODO: description'''
    return os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), fileName))
  
  def PrepareFileName(self, groupId, artifactId, version, type): 
    '''TODO: description'''
    if groupId is None:
      groupId = artifactId
    dirName = '.repository/%s/%s/%s' % (groupId.replace('.', '/'), artifactId, str(version))
    fileName = os.path.join(dirName, '%s-%s.%s' % (artifactId, str(version), str(type)))
    return self.PrepareRealFileName(fileName) 
  
  def GetFileMarker(self, fileName):
    timestamp = None
    sha1 = None
    try:
      with open(fileName + self._AttaDataExt(), 'r') as lf:
        lines = lf.readlines()
        if len(lines) > 0:
          timestamp = lines[0].strip()
        if len(lines) > 1:
          sha1 = lines[1].strip()
        lf.close()
    except:
      return None
    else:
      return (timestamp, sha1)
    
  def Get(self, groupId, artifactId, version, type, store = None, **tparams):
    '''TODO: description'''
    fileName = self.PrepareFileName(groupId, artifactId, version, type)
    if not os.path.exists(fileName):
      raise AttaError(self, "Can't find: " + IRepository.DisplayName(groupId, artifactId, version, type))
    
    if store is not None:
      self.Log('Checking: %s in: %s' % (IRepository.DisplayName(groupId, artifactId, version, type), store._Name()), level = LogLevel.VERBOSE)
      timestamp, sha1 = self.GetFileMarker(fileName)
      fileInStore = store.Check(groupId, artifactId, version, type, timestamp, **tparams)
      if fileInStore is None:
        self.Log('Uploading to: ' + store._Name(), level = LogLevel.INFO)
        with open(fileName, 'rb') as f:
          store.Put(f, timestamp, groupId, artifactId, version, type, **tparams)
      else:
        if fileName == fileInStore[0]:
          self.Log("Unable to store: %s in the same repository, from which it is pulled." % IRepository.DisplayName(groupId, artifactId, version, type), level = LogLevel.WARNING)

    return [fileName]
  
  # TODO: uzyc wzorca Strategy do implementacji Check
  def Check(self, groupId, artifactId, version, type, timestamp, **tparams):
    '''returns: None or [fileName, fileSize, storedTimestamp]'''
    fileName = self.PrepareFileName(groupId, artifactId, version, type)
    
    if not os.path.exists(fileName):
      return None
    
    storedTimestamp, storedSha1 = self.GetFileMarker(fileName)
    if storedTimestamp is None:
      return None
    
    # if the given timestamp isn't equal to the local file timestamp (stored with the file: see Put method) then return None 
    if timestamp is not None:
      if long(timestamp) != long(storedTimestamp):
        return None
      else:
        os.utime(fileName, None) # equivalent: touch

    # if the local file was stored earlier (modification time) than _LifeTime then return None
    fileTime = datetime.fromtimestamp(os.path.getmtime(fileName))
    if datetime.now() - fileTime > self._LifeTime():
      return None
     
    return [fileName, OS.FileSize(fileName), storedTimestamp]
  
  def Put(self, f, timestamp, groupId, artifactId, version, type, **tparams):
    '''returns: None or [fileName, fileSize]'''
    fileName = self.PrepareFileName(groupId, artifactId, version, type)
    self.Log('Takes: %s' % IRepository.DisplayName(groupId, artifactId, version, type), level = LogLevel.INFO)
    
    OS.MakeDirs(os.path.dirname(fileName))
    
    # TODO: handle f if string (fileName) or list (fileNames or file-like objects)
    
    with open(fileName, 'wb') as lf:
      lf.write(f.read())
      lf.close()
    
    with open(fileName + self._AttaDataExt(), 'wb') as lf:
      lf.write(str(timestamp))
      lf.write('\n')
      lf.write(OS.FileHash(fileName, hashlib.sha1()))
      lf.close()
        
    return [fileName, OS.FileSize(fileName)]
  
  def _Name(self):
    name = Task._Name(self)
    return 'Local.' + name
  
  '''private section'''
  
  def _AttaDataExt(self):
    return '.atta'
  
  def _LifeTime(self):
    return timedelta(days = 14)
    #return timedelta(seconds = 5)
