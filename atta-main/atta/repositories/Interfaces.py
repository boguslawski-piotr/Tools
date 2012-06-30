'''.. no-user-reference:'''
import os
import atta.tools.OS as OS

class PackageId:
  '''TODO: description'''
  def __init__(self, groupId, artifactId, version, type_, timestamp = None, sha1 = None):
    self.groupId = groupId
    self.artifactId = artifactId
    if self.groupId is None:
      self.groupId = self.artifactId
    self.version = version
    self.type_ = type_
    self.timestamp = timestamp
    self.sha1 = sha1
    
  def __eq__(self, other):
    return str(self) == str(other)
  
  def __cmp__(self, other):
    raise RuntimeError("PackageId objects can be compared only to the fact equality.")
  
  def __nonzero__(self):
    return self.groupId is not None and self.artifactId is not None and self.version is not None and self.type_ is not None
  
  def __str__(self):
    return '%s:%s.%s:%s' % (str(self.groupId), str(self.artifactId), str(self.type_), str(self.version))

  def FileName(self):
    '''TODO: description'''
    dirName = '%s/%s/%s' % (str(self.groupId).replace('.', '/'), str(self.artifactId), str(self.version))
    return os.path.join(dirName, '%s-%s.%s' % (str(self.artifactId), str(self.version), str(self.type_)))
  
  @staticmethod
  def FromStr(packageStrId):
    '''TODO: description'''
    groupId = artifactId = type_ = version = None
    try:
      items = packageStrId.split(':')
      if len(items) >= 3:
        groupId = items[0]
        del items[0]
      artifactId = OS.Path.RemoveExt(items[0])
      type_ = OS.Path.Ext(items[0])
      version = items[1]
    except:
      pass
    return PackageId(groupId, artifactId, version, type_)
  
class IRepository:
  '''TODO: description'''
  class Dictionary:
    '''TODO: description'''
    dependsOn  = 'dependsOn'
    repository = 'repository'
    package    = 'package'
    groupId    = 'groupId'
    artifactId = 'artifactId'
    version    = 'version'
    type       = 'type'
    putIn      = 'putIn'
    
  def Get(self, packageId, store = None, **tparams):
    '''TODO: description'''
    pass
  
  def Check(self, packageId, **tparams):
    '''TODO: description'''
    pass
  
  def Put(self, f, packageId, **tparams):
    '''TODO: description'''
    pass
  
  def Clean(self, packageId, **tparams): 
    '''TODO: description'''
    pass
    
  def _Name(self):
    '''TODO: description'''
    pass
  
    