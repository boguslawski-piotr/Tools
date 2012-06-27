import sys
from Interfaces import PackageId, IRepository

class Resolver:
  '''TODO: description'''
  def __init__(self):
    self.Clear()
  
  def Resolve(self, data):
    rc = False
    for e in data:
      if e.has_key(IRepository.Dictionary.dependsOn):
        # recursively resolve the dependencies
        self.Resolve(e[IRepository.Dictionary.dependsOn])
      
      repositoryName = e.get(IRepository.Dictionary.repository)
      if repositoryName is None:
        continue
      
      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository()
      
      packageStrId = e.get(IRepository.Dictionary.package)
      if packageStrId is not None:
        packageId = PackageId.FromStr(packageStrId)
      else:
        packageId = PackageId(e.get(IRepository.Dictionary.groupId), e.get(IRepository.Dictionary.artifactId), e.get(IRepository.Dictionary.version), e.get(IRepository.Dictionary.type))
      
      store = None
      storeName = e.get(IRepository.Dictionary.putIn)
      if storeName is not None:
        __import__(storeName)
        store = sys.modules[storeName].Repository()
      
      result = repository.Get(packageId, store, data = e)
      if result is not None and len(result) > 0:
        self.result += result
        rc = True
      else:
        pass
        # TODO: handle ifNotExists
    
    return rc
    
  def Result(self):
    self.result = list(set(self.result))  # remove duplicates
    return self.result
  
  def Clear(self):
    self.result = []
    