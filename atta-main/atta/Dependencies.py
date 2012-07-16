"""TODO: description"""
import sys

from .tools.Misc import RemoveDuplicates
from .repositories.Package import PackageId
from .repositories import ArtifactNotFoundError
from . import Dict, AttaError

class Resolver:
  """TODO: description"""
  def __init__(self):
    self.Clear()

  def Resolve(self, data, scope = Dict.Scopes.compile, defaultRepository = None):
    """TODO: description"""
    rc = False
    for e in data:
      if isinstance(e, basestring):
        e = dict(package = e)

      if Dict.dependsOn in e:
        # Recursively resolve the dependencies.
        self.Resolve(e[Dict.dependsOn], scope, defaultRepository)

      repositoryName = e.get(Dict.repository)
      if not repositoryName:
        if not defaultRepository:
          raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
        repositoryName = defaultRepository
      if not isinstance(repositoryName, basestring):
        repositoryName = repositoryName.__name__

      packageStrId = e.get(Dict.package)
      if packageStrId:
        package = PackageId.FromStr(packageStrId)
      else:
        package = PackageId(e.get(Dict.groupId), e.get(Dict.artifactId), e.get(Dict.version), e.get(Dict.type))
      package.optional = e.get(Dict.optional, False)
      package.scope = e.get(Dict.scope, Dict.Scopes.compile)
      if package.scope != scope:
        continue

      __import__(repositoryName)
      repository = sys.modules[repositoryName].Repository(e)

      store = None
      storeName = e.get(Dict.putIn)
      if storeName:
        storeData = None
        if isinstance(storeName, dict):
          storeData = storeName
          storeName = storeData.get(Dict.repository)
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
      finally:
        repository = None

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
