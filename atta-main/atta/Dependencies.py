import sys

from atta.repositories.Base import ARepository
from repositories.Package import PackageId
from repositories import ArtifactNotFoundError

class Resolver:
  '''TODO: description'''
  def __init__(self):
    self.Clear()
  
  def Resolve(self, data):
    rc = False
    for e in data:
      if ARepository.Dictionary.dependsOn in e:
        # recursively resolve the dependencies
        self.Resolve(e[ARepository.Dictionary.dependsOn])
      
      repositoryName = e.get(ARepository.Dictionary.repository)
      if repositoryName is None:
        continue
      
      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)
      
      packageStrId = e.get(ARepository.Dictionary.package)
      if packageStrId is not None:
        packageId = PackageId.FromStr(packageStrId)
      else:
        packageId = PackageId(e.get(ARepository.Dictionary.groupId), 
                              e.get(ARepository.Dictionary.artifactId), 
                              e.get(ARepository.Dictionary.version), 
                              e.get(ARepository.Dictionary.type))
      
      store = None
      storeName = e.get(ARepository.Dictionary.putIn)
      if storeName is not None:
        storeData = None
        if isinstance(storeName, dict):
          storeData = storeName
          storeName = storeData.get(ARepository.Dictionary.repository)
        __import__(storeName)
        store = sys.modules[storeName].Repository(storeData)
      
      try:
        result = repository.Get(packageId, store)
      except ArtifactNotFoundError:
        if ARepository.Dictionary.ifNotExists in e:
          rc = self.Resolve(e[ARepository.Dictionary.ifNotExists])
        else:
          raise
      else:  
        if result is not None and len(result) > 0:
          self.result += result
          rc = True
        else:
          if ARepository.Dictionary.ifNotExists in e:
            rc = self.Resolve(e[ARepository.Dictionary.ifNotExists])
      finally:
        repository = None
    
    return rc
    
  def Result(self):
    self.result = list(set(self.result))  # remove duplicates
    return self.result
  
  def Clear(self):
    self.result = []
    