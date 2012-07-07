'''TODO: description'''
import sys

from .repositories.Package import PackageId
from .repositories import ArtifactNotFoundError
from . import Dict

class Resolver:
  '''TODO: description'''
  def __init__(self):
    self.Clear()
  
  def Resolve(self, data, scope = Dict.Scopes.compile):
    rc = False
    for e in data:
      if Dict.dependsOn in e:
        # Recursively resolve the dependencies.
        self.Resolve(e[Dict.dependsOn], scope)
      
      repositoryName = e.get(Dict.repository)
      if repositoryName is None:
        continue
      
      packageScope = e.get(Dict.scope, Dict.Scopes.compile)
      if packageScope != scope:
        continue
      
      packageStrId = e.get(Dict.package)
      if packageStrId is not None:
        packageId = PackageId.FromStr(packageStrId)
      else:
        packageId = PackageId(e.get(Dict.groupId), 
                              e.get(Dict.artifactId), 
                              e.get(Dict.version), 
                              e.get(Dict.type))
      
      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)

      store = None
      storeName = e.get(Dict.putIn)
      if storeName is not None:
        storeData = None
        if isinstance(storeName, dict):
          storeData = storeName
          storeName = storeData.get(Dict.repository)
        __import__(storeName)
        store = sys.modules[storeName].Repository(storeData)
      
      try:
        result = repository.Get(packageId, scope, store)
      except ArtifactNotFoundError:
        if Dict.ifNotExists in e:
          rc = self.Resolve(e[Dict.ifNotExists])
        else:
          raise
      else:  
        if result is not None and len(result) > 0:
          self.result += result
          if not Dict.scope in dir(packageId):
            packageId.scope = scope
          self.resultPackages.append(packageId)
          rc = True
        else:
          if Dict.ifNotExists in e:
            rc = self.Resolve(e[Dict.ifNotExists])
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
