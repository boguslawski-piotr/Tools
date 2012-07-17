"""TODO: description"""
import sys

from .tools.internal.Misc import AttaClassOrModule
from .tools.Misc import isstring, RemoveDuplicates
from .repositories import ArtifactNotFoundError
from . import Dict, AttaError, OS, PackageId

class Resolver:
  """TODO: description"""
  def __init__(self):
    self.Clear()

  def Resolve(self, data, scope = Dict.Scopes.default, defaultRepository = None):
    """TODO: description"""
    rc = False
    for e in data:
      if isstring(e):
        e = dict(package = e)

      if Dict.dependsOn in e:
        # Recursively resolve the dependencies.
        self.Resolve(e[Dict.dependsOn], scope, defaultRepository)

      repositoryName = e.get(Dict.repository)
      if not repositoryName:
        if not defaultRepository:
          raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
        repositoryName = defaultRepository
      if not isstring(repositoryName):
        repositoryName = repositoryName.__name__
      repositoryName = AttaClassOrModule(repositoryName)

      packageStrId = e.get(Dict.package)
      if packageStrId:
        package = PackageId.FromStr(packageStrId)
      else:
        package = PackageId(e.get(Dict.groupId), e.get(Dict.artifactId), e.get(Dict.version), e.get(Dict.type))
      package.scope = e.get(Dict.scope, Dict.Scopes.default)
      if package.scope != scope:
        continue
      package.exclusions = OS.Path.AsList(e.get(Dict.exclusions), ',')
      package.optional = e.get(Dict.optional, False)

      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)

      store = None
      storeName = e.get(Dict.putIn)
      if storeName:
        storeData = None
        if isinstance(storeName, dict):
          storeData = storeName
          storeName = storeData.get(Dict.repository)
        storeName = AttaClassOrModule(storeName)
        __import__(storeName)
        store = sys.modules[storeName].Repository(storeData)

      try:
        result = repository.Get(package, scope, store)
      except ArtifactNotFoundError:
        if Dict.ifNotExists in e:
          rc = self.Resolve(e[Dict.ifNotExists], scope, defaultRepository)
        else:
          raise
      else:
        if result:
          rc = True
          self.result += result
          self.resultPackages.append(package)
        else:
          if Dict.ifNotExists in e:
            rc = self.Resolve(e[Dict.ifNotExists], scope, defaultRepository)

    return rc

  def Result(self):
    self.result = RemoveDuplicates(self.result)
    return self.result

  def ResultPackages(self):
    # TODO: remove duplicates
    return self.resultPackages

  def Clear(self):
    self.result = []
    self.resultPackages = []
