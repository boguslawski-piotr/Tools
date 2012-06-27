import os
import shutil
import hashlib
from datetime import datetime, timedelta

import atta.tools.OS as OS
from ..tasks.Base import Task
from ..tools.Misc import LogLevel
from ..tools.Properties import Properties
from ..loggers import Compact
from ..Interfaces import IRepository
from atta import AttaError

class Repository(IRepository, Task):
  '''TODO: description'''

  def PrepareRealFileName(self, fileName):
    '''TODO: description'''
    return os.path.normpath(os.path.join(os.path.expanduser('~'), self._AttaDataExt(), fileName))
  
  def PrepareFileName(self, packageId): 
    '''TODO: description'''
    fileName = os.path.join('.repository', packageId.FileName())
    return self.PrepareRealFileName(fileName) 
  
  def GetFileMarker(self, fileName):
    '''TODO: description'''
    try:
      with Properties.Open(fileName + self._AttaDataExt()) as p:
        timestamp = p.Get('timestamp', None)
        sha1 = p.Get('sha1', None)
    except:
      return (None, None)
    else:
      return (timestamp, sha1)
    
  def PutFileMarker(self, fileName, packageId):
    '''TODO: description'''
    with Properties.Create(fileName + self._AttaDataExt()) as p:
      p.Set('timestamp', packageId.timestamp)
      p.Set('sha1', OS.FileHash(fileName, hashlib.sha1()))
      p.Save()
      
  def Get(self, packageId, store = None, **tparams):
    '''TODO: description'''
    fileName = self.PrepareFileName(packageId)
    if not os.path.exists(fileName):
      raise AttaError(self, "Can't find: " + str(packageId))
    
    if store is not None:
      packageId.timestamp, packageId.sha1 = self.GetFileMarker(fileName)
      fileInStore = store.Check(packageId, **tparams)
      if fileInStore is None:
        self.Log('Uploading: %s to: %s' %(str(packageId), store._Name()), level = LogLevel.INFO)
        with open(fileName, 'rb') as f:
          store.Put(f, packageId, **tparams)
      else:
        if fileName == fileInStore[0]:
          self.Log("Unable to store: %s in the same repository, from which it is pulled." % str(packageId), level = LogLevel.WARNING)

    return [fileName]
  
  # TODO: uzyc wzorca Strategy do implementacji Check
  def Check(self, packageId, **tparams):
    '''returns: None or [fileName, fileSize, storedTimestamp]'''
    fileName = self.PrepareFileName(packageId)
    self.Log('Checking: %s' % str(packageId), level = LogLevel.VERBOSE)
    
    if not os.path.exists(fileName):
      return None
    
    storedTimestamp, storedSha1 = self.GetFileMarker(fileName)
    if storedTimestamp is None:
      return None
    
    # if the given timestamp isn't equal to the local file timestamp (stored with the file: see Put method) then return None 
    if packageId.timestamp is not None:
      if long(packageId.timestamp) != long(storedTimestamp):
        return None
      else:
        os.utime(fileName, None) # equivalent: touch

    # if the local file was stored earlier (modification time) than _LifeTime then return None
    fileTime = datetime.fromtimestamp(os.path.getmtime(fileName))
    if datetime.now() - fileTime > self._LifeTime():
      return None
     
    return [fileName, OS.FileSize(fileName), storedTimestamp]
  
  def Put(self, f, packageId, **tparams):
    '''returns: None or [fileName, fileSize]'''
    fileName = self.PrepareFileName(packageId)
    self.Log('Takes: %s' % str(packageId), level = LogLevel.INFO)
    
    OS.MakeDirs(os.path.dirname(fileName))
    
    # TODO: handle f if string (fileName) or list (fileNames or file-like objects)
    
    with open(fileName, 'wb') as lf:
      lf.write(f.read())
      lf.close()
    
    self.PutFileMarker(fileName, packageId)
        
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
