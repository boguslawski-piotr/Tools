"""TODO: description"""
import sys

from .tools.internal.Misc import AttaClassOrModule
from .tools.Misc import isstring, RemoveDuplicates
from .repositories import ArtifactNotFoundError, Base
from . import Dict, AttaError, LogLevel, OS, PackageId, Task
from . import Activity

class Resolver(Task):
  """TODO: description"""
  def __init__(self):
    self.Clear()

  def Resolve(self, data, scope = Dict.Scopes.default, defaultRepository = None):
    """TODO: description"""
    failOnError = True
    rc = False
    for e in data:
      try:
        if isstring(e):
          e = dict(package = e)
        failOnError = e.get(Dict.paramFailOnError, True)

        if Dict.dependsOn in e:
          # Recursively resolve the dependencies.
          self.Resolve(e[Dict.dependsOn], scope, defaultRepository)

        # Create (or get) package object.
        packageStrId = e.get(Dict.package)
        if packageStrId is not None:
          if isinstance(packageStrId, PackageId):
            package = packageStrId
          else:
            package = PackageId.FromStr(packageStrId)
        else:
          package = PackageId(e.get(Dict.groupId), e.get(Dict.artifactId), e.get(Dict.version), e.get(Dict.type))

        # Check whether the definition applies to the current scope.
        if not package.scope: package.scope = e.get(Dict.scope, Dict.Scopes.default)
        if package.scope != scope:
          continue

        # Get additional package properties.
        if not package.exclusions: package.exclusions = OS.Path.AsList(e.get(Dict.exclusions), ',')
        if not package.optional: package.optional = e.get(Dict.optional, False)
        if not package.downloadUrl: package.downloadUrl = e.get(Dict.downloadUrl, None)
        if not package.baseUrl: package.baseUrl = e.get(Dict.baseUrl, None)
        if not package.fileNames: package.fileNames = e.get(Dict.fileNames, None)

        # Prepare repository object.
        repositoryName = e.get(Dict.repository)
        if not repositoryName:
          if not defaultRepository:
            raise AttaError(self, Dict.errNotSpecified.format(Dict.repository))
          repositoryName = defaultRepository
        if Base.ARepository.IsMyInstance(repositoryName):
          repository = repositoryName
        elif Base.ARepository.IsMySubclass(repositoryName):
          repository = repositoryName(**e)
        else:
          if not isstring(repositoryName):
            repositoryName = repositoryName.__name__
          repositoryName = AttaClassOrModule(repositoryName)
          __import__(repositoryName)
          repository = sys.modules[repositoryName].Repository(**e)

        # Prepare store object if specified.
        store = None
        storeName = e.get(Dict.putIn)
        if storeName:
          if Base.ARepository.IsMyInstance(storeName):
            store = storeName
          else:
            storeData = {}
            if Base.ARepository.IsMySubclass(storeName):
              store = storeName()
            else:
              if isinstance(storeName, dict):
                storeData = storeName
                storeName = storeData.get(Dict.repository)
              storeName = AttaClassOrModule(storeName)
              if not storeName:
                raise AttaError(self, Dict.errNotSpecified.format(Dict.repository + " in 'putIn' entry"))
              __import__(storeName)
              store = sys.modules[storeName].Repository(**storeData)

        # Get the artifact file names.
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

      except Exception as E:
        if failOnError:
          raise
        else:
          self.Log(str(E), level = LogLevel.ERROR)

    return rc

  def Result(self):
    self.result = RemoveDuplicates(self.result)
    return self.result

  def ResultPackages(self):
    self.resultPackages = RemoveDuplicates(self.resultPackages)
    return self.resultPackages

  def Clear(self):
    self.result = []
    self.resultPackages = []
