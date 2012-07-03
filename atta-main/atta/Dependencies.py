import sys

from repositories.Package import PackageId
from repositories import ArtifactNotFoundError
import Dictionary

class Resolver:
  '''TODO: description'''
  def __init__(self):
    self.Clear()
  
  def Resolve(self, data, scope = Dictionary.Scopes.compile):
    rc = False
    for e in data:
      if Dictionary.dependsOn in e:
        # Recursively resolve the dependencies.
        self.Resolve(e[Dictionary.dependsOn], scope)
      
      repositoryName = e.get(Dictionary.repository)
      if repositoryName is None:
        continue
      
      packageScope = e.get(Dictionary.scope, Dictionary.Scopes.compile)
      if packageScope != scope:
        continue
      
      packageStrId = e.get(Dictionary.package)
      if packageStrId is not None:
        packageId = PackageId.FromStr(packageStrId)
      else:
        packageId = PackageId(e.get(Dictionary.groupId), 
                              e.get(Dictionary.artifactId), 
                              e.get(Dictionary.version), 
                              e.get(Dictionary.type))
      
      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)

      store = None
      storeName = e.get(Dictionary.putIn)
      if storeName is not None:
        storeData = None
        if isinstance(storeName, dict):
          storeData = storeName
          storeName = storeData.get(Dictionary.repository)
        __import__(storeName)
        store = sys.modules[storeName].Repository(storeData)
      
      try:
        result = repository.Get(packageId, scope, store)
      except ArtifactNotFoundError:
        if Dictionary.ifNotExists in e:
          rc = self.Resolve(e[Dictionary.ifNotExists])
        else:
          raise
      else:  
        if result is not None and len(result) > 0:
          self.result += result
          if not Dictionary.scope in dir(packageId):
            packageId.scope = scope
          self.resultPackages.append(packageId)
          rc = True
        else:
          if Dictionary.ifNotExists in e:
            rc = self.Resolve(e[Dictionary.ifNotExists])
      finally:
        repository = None
    
    return rc
    
  def Result(self):
    self.result = list(set(self.result))  # remove duplicates
    return self.result
  
  def ResultPackages(self):
    # TODO: remove duplicates
    return self.resultPackages

  def Clear(self):
    self.result = []
    self.resultPackages = []
