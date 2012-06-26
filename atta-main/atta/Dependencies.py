import sys
from Interfaces import IRepository

class XXX:
  '''TODO: description'''
  dependsOn  = 'dependsOn'
  repository = 'repository'
  package    = 'package'
  groupId    = 'groupId'
  artifactId = 'artifactId'
  version    = 'version'
  type       = 'type'
  putIn      = 'putIn'
  
class Resolver:
  '''TODO: description'''
  def __init__(self):
    self.Clear()
  
  def Resolve(self, data):
    rc = False
    for e in data:
      if e.has_key(XXX.dependsOn):
        # recursively resolve the dependencies
        self.Resolve(e[XXX.dependsOn])
      
      repositoryName = e.get(XXX.repository)
      if repositoryName is None:
        continue
      
      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository()
      
      package = e.get(XXX.package)
      if package is not None:
        groupId, artifactId, type, version = IRepository.ResolveDisplayName(package)
      else:
        groupId = e.get(XXX.groupId)
        artifactId = e.get(XXX.artifactId)
        version = e.get(XXX.version)
        type = e.get(XXX.type)
      
      store = None
      storeName = e.get(XXX.putIn)
      if storeName is not None:
        __import__(storeName)
        store = sys.modules[storeName].Repository()
      
      result = repository.Get(groupId, artifactId, version, type, store, data = e)
      if result is not None and len(result) > 0:
        self.result += result
        rc = True
      else:
        pass
        # TODO: handle ifNotExists
    
    return rc
    
  def Result(self):
    return self.result
  
  def Clear(self):
    self.result = []
    