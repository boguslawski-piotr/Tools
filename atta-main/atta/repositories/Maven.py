""".. Remote: TODO"""
import urllib2
import cStringIO
import os

from ..tools.internal.Misc import ObjectFromClass
from ..tools.Misc import NamedFileLike, RemoveDuplicates, strip
from ..tools import DefaultVarsExpander
from .. import AttaError, Dict, LogLevel, OS, Xml, PackageId
from . import ArtifactNotFoundError, Styles, Remote

class Repository(Remote.Repository):
  """TODO: description
  """
  def __init__(self, **tparams):
    Remote.Repository.__init__(self, **tparams)
    self._styleImpl = ObjectFromClass(Styles.Maven)
    self.maxRetries = self.data.get(Dict.maxRetries, 1)

  def GetFileMarker(self, fileName, forGet):
    try:
      sha1 = self.GetFileContents(OS.Path.JoinExt(fileName, Dict.sha1Ext))
      sha1 = sha1[:40]
      return sha1, sha1
    except Exception:
      return None, None

  def PutMarkerFile(self, fileName, fileSha1, package):
    self.PutFileContents(str(fileSha1), OS.Path.JoinExt(fileName, Dict.sha1Ext))

  def PutInfoFile(self, package, storedFileNames):
    # Atta does not create or modify the file: _maven.repositories
    pass

  def CompleteFileName(self, fileName):
    return os.path.normpath(os.path.join(os.path.expanduser('~'), '.m2', fileName))

  def GetAll(self, package, forGet):
    result = [self.PrepareFileName(package)]
    if package.type != Dict.pom:
      result.append(self.PrepareFileName(PackageId.FromPackage(package, type = Dict.pom)))
    return result

  def _Get(self, package, scope, store, resolvedPackages):
    # First, see in the store (cache) if the required
    # files (for package and its dependencies) are all up to date.
    problem = False
    filesInStore = store.Check(package, scope)
    if filesInStore is None:
      # If something is obsolete, missing or corrupted then refresh the store.
      download = True
      filesInStore = []

      # Get the dependencies.
      pom = Repository.GetPOM(package, refresh = True, logFn = self.Log)
      if pom:
        packages = Repository.GetDependenciesFromPOM(package, pom,
                                                     Dict.Scopes.map2POM.get(scope, []),
                                                     self.OptionalAllowed(), logFn = self.Log)
        for p in packages:
          if not package.Excludes(p):
            if p not in resolvedPackages:
              resolvedPackages.append(p)
              filesInStore += self._Get(p, scope, store, resolvedPackages)
        if packages:
          # After downloading all the dependencies, check the store third time.
          # This is intended to minimize the amount of downloads.
          filesInStore2 = store.Check(package, scope)
          if filesInStore2:
            download = False
            filesInStore = filesInStore2

      if download:
        # Get the artifact and put it into the store.
        self.Log(Dict.msgSendingXToY % (package.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
        filesToDownload = []
        if pom:
          filesToDownload.append(NamedFileLike(Styles.Maven().FileName(PackageId.FromPackage(package, type = Dict.pom)),
                                 cStringIO.StringIO(pom)))
        if package.type != Dict.pom or not pom:
          f = Repository.GetArtifactFile(package, pom, store.PrepareFileName(package), self.maxRetries, self.Log)
          if f is not None:
            filesToDownload.append(NamedFileLike(Styles.Maven().FileName(package), f))
          else:
            problem = True
        if not problem and filesToDownload:
          try:
            filesInStore += store.Put('', filesToDownload, package)
          except Exception as E:
            self.Log(Dict.errXWhileSavingY % (str(E), str(package)), level = LogLevel.ERROR)
            problem = True

    # Check the results.
    if not filesInStore or problem:
      if not package.optional:
        raise ArtifactNotFoundError(self, Dict.errFailedToAssembleX % str(package))
      else:
        filesInStore = []

    # Return the package files and its dependencies files.
    filesInStore = RemoveDuplicates(filesInStore)
    self.Log(Dict.msgReturns % OS.Path.FromList(filesInStore), level = LogLevel.DEBUG)
    return filesInStore

  def DefaultStore(self):
    return Repository(lifeTime = None)

  def Get(self, package, scope, store = None):
    """TODO: description
     returns list (of strings: fileName) of locally available files
    """
    # Check parameters.
    if not bool(package.type):
      package.type = Dict.jar
    if not package:
      raise AttaError(self, Dict.errPackageNotComplete % str(package))

    return Remote.Repository.Get(self, package, scope, store)

  #
  # Resolvers

  # TODO: give more accurate name
  class IResolver:
    """TODO: description"""
    def PackageUrl(self, package):
      assert False

  class Central(IResolver):
    """TODO: description"""
    def __init__(self, baseUrl = 'http://search.maven.org/'):
      self.baseUrl = baseUrl
      if not self.baseUrl.endswith('/'):
        self.baseUrl += '/'

    def PackagePath(self, package):
      return '{0}/{1}/{2}/{3}'.format(
        str(package.groupId).replace('.', '/'), package.artifactId, package.version, package.AsFileName(Styles.Maven))

    def PackageUrl(self, package):
      return self.baseUrl + 'remotecontent?filepath=' + self.PackagePath(package)

  class Sonatype(Central):
    """TODO: description"""
    def __init__(self, baseUrl = 'https://oss.sonatype.org/content/repositories/public/'):
      Repository.Central.__init__(self, baseUrl)

    def PackageUrl(self, package):
      url = self.baseUrl + self.PackagePath(package)
      return url

  class Local(Central):
    """TODO: description"""
    def __init__(self, baseUrl = 'file://~/.m2/repository'):
      Repository.Central.__init__(self, baseUrl)

    def PackageUrl(self, package):
      return os.path.normpath(self.baseUrl.replace('~', os.path.expanduser('~')) + self.PackagePath(package))

  #: TODO: description
  resolvers = [Central()]

  @staticmethod
  def GetArtifactFile(package, pom = None, excludedUrl = None, maxRetries = 1, logFn = None):
    """TODO: description"""
    # Try to download the file from the repository(ies).
    resolvers = Repository.resolvers
    for resolver in resolvers:
      url = resolver.PackageUrl(package)
      if url and (not excludedUrl or url.find(excludedUrl) < 0):
        if logFn: logFn(Dict.msgDownloading % url, level = LogLevel.VERBOSE)
        try:
          return Remote.Repository.GetFileLikeForUrl(url, maxRetries, logFn = logFn)
        except urllib2.URLError:
          continue

    # If the package is not found in any repository or when the error occurred,
    # check the alternate place(s) from which you can download the file.

    def _download(url):
      if url:
        if logFn: logFn(Dict.msgDownloading % url, level = LogLevel.VERBOSE)
        try:
          return Remote.Repository.GetFileLikeForUrl(url, maxRetries, logFn = logFn)
        except urllib2.HTTPError:
          pass
      return None

    if pom:
      # If is specified in the POM file.
      f = _download(Repository.GetArtifactUrlFromPOM(pom, logFn))
      if f is not None:
        return f
    if package.downloadUrl:
      # If is specified in the package definition.
      if isinstance(package.downloadUrl, Repository.IResolver):
        return _download(package.downloadUrl.PackageUrl(package))
      else:
        return _download(package.downloadUrl)

    return None

  #
  # POM support

  _pomCache = {}

  @staticmethod
  def GetPOMCacheKey(package):
    """TODO: description"""
    return str(package)

  @staticmethod
  def GetPOMFromCache(package, logFn = None):
    """TODO: description"""
    key = Repository.GetPOMCacheKey(package)
    if key in Repository._pomCache:
      if logFn: logFn('Getting: %s from cache.' % str(package), level = LogLevel.DEBUG)
      return Repository._pomCache[key]
    return None

  @staticmethod
  def PutPOMIntoCache(package, f, logFn = None):
    """TODO: description"""
    key = Repository.GetPOMCacheKey(package)
    if f is not None:
      if 'read' in dir(f):
        Repository._pomCache[key] = f.read()
      else:
        Repository._pomCache[key] = f

  @staticmethod
  def GetPOM(package, refresh = False, logFn = None):
    """Gets the POM file.
       The function uses the local impermanent cache.
       Returns the POM contents or None."""
    package = PackageId.FromPackage(package, type = Dict.pom)
    pomFile = None if refresh else Repository.GetPOMFromCache(package, logFn)
    if pomFile is None:
      Repository.PutPOMIntoCache(package,
                                 Repository.GetArtifactFile(package, None, None, 1, logFn), logFn)
    return Repository.GetPOMFromCache(package, logFn)

  @staticmethod
  def GetPOMEx(package, pom, logFn = None):
    """Checks if the *pom* is the callable used to download contents of a POM file.
       If so, use it and try to retrieve data.
       If the download did not succeed then try again using internal method.
       Returns a tuple (*function*, *pom*) where *function* is a callable
       which you can use to download next POM file and *pom* points to the
       contents of the file or None."""
    getPOMFn = Repository.GetPOM
    if pom and '__call__' in dir(pom):
      getPOMFn = pom
      pom = getPOMFn(package, logFn = logFn)
      if pom is None and getPOMFn != Repository.GetPOM:
        getPOMFn = Repository.GetPOM
        pom = getPOMFn(package, logFn = logFn)
    return getPOMFn, pom

  @staticmethod
  def GetArtifactUrlFromPOM(pom, logFn = None):
    """TODO: description"""
    if pom:
      if not isinstance(pom, Xml):
        pom = Xml(pom)
      url = pom.values(Dict.distributionManagement + '/' + Dict.downloadUrl, stripfn = strip)
      if len(url) > 0:
        return url[0][Dict.downloadUrl]
    return None

  @staticmethod
  def _GetPropertiesFromPOM(package, pom, logFn = None):
    # Prepare POM contents.
    getPOMFn, pom = Repository.GetPOMEx(package, pom, logFn)
    if pom is None:
      return []
    if not isinstance(pom, Xml):
      pom = Xml(pom)

    # Check and handle <parent> section.
    props = []
    parent = pom.values(Dict.parent, stripfn = strip)
    if len(parent) > 0:
      for p in parent:
        if not Dict.relativePath in p:
          # Recursively process the entire tree.
          parentPackage = PackageId.FromDict(p, type = Dict.pom)
          props += Repository._GetPropertiesFromPOM(parentPackage, getPOMFn, logFn)

    # Handle <properties> section.
    props += pom.values(Dict.properties, stripfn = strip)

    # Handle 'coordinates' and sets ${project.xxx} properties.
    def _ProjectProps(name):
      p = pom.values(name, stripfn = strip)
      if p:
        p[0][Dict.project + '.' + name] = p[0][name]
      return p
    props += _ProjectProps(Dict.groupId)
    props += _ProjectProps(Dict.artifactId)
    props += _ProjectProps(Dict.packaging)
    props += _ProjectProps(Dict.version)

    if logFn: logFn(Dict.msgLoadedPropertiesForX % package.AsStrWithoutType(), level = LogLevel.DEBUG)
    return props

  @staticmethod
  def GetPropertiesFromPOM(package, pom, logFn = None):
    """TODO: description"""
    props = Repository._GetPropertiesFromPOM(package, pom, logFn)
    d = {}
    for p in props:
      d.update(p)
    return d

  @staticmethod
  def _GetDependenciesFromPOM(package, pom, props, scopes, includeOptional = False, logFn = None):
    """TODO: description"""
    assert scopes is not None
    assert isinstance(scopes, list)

    # Prepare POM contents.
    getPOMFn, pom = Repository.GetPOMEx(package, pom, logFn = logFn)
    if pom is None:
      return [], []
    if not isinstance(pom, Xml):
      pom = Xml(pom)

    dependencies = []
    dmDependencies = []

    # Handle <parent> section.
    parent = pom.values(Dict.parent, stripfn = strip)
    if len(parent) > 0:
      for p in parent:
        if not Dict.relativePath in p:
          # Recursively collect dependencies from the entire tree.
          parentPackage = PackageId.FromDict(p, type = Dict.pom)
          parentDependencies, parentDmDependencies = Repository._GetDependenciesFromPOM(parentPackage,
                                                            getPOMFn, props, scopes, includeOptional, logFn)
          dependencies += parentDependencies
          dependencies += [parentPackage]
          dmDependencies += parentDmDependencies

    expander = DefaultVarsExpander.Expander()

    def _PreparePackagesFromDependencies(depSrc, ignoreScopes = False):
      depDest = []
      for d in depSrc:
        dependPackage = PackageId(type = Dict.jar)

        # Collect package information from <dependency> section.
        for i in list(d):
          ltag = i.tag.lower()
          if ltag == Dict.exclusions:
            # Handle <exclusions> section.
            for es in list(i):
              excludedPackage = PackageId()
              for e in list(es):
                text = expander.Expand(e.text, **props)
                excludedPackage.__setattr__(e.tag, text)
              dependPackage.exclusions.append(excludedPackage)
          else:
            if not includeOptional:
              if ltag == Dict.optional:
                if i.text.lower().strip() == Dict.true:
                  dependPackage = None
                  break
            text = expander.Expand(i.text, **props)
            dependPackage.__setattr__(i.tag, text)

        if dependPackage is None:
          continue

        # Search for the missing properties in the definitions from parents.
        for parent in reversed(dmDependencies):
          if parent.groupId == dependPackage.groupId and parent.artifactId == dependPackage.artifactId:
            if not dependPackage.version: dependPackage.version = parent.version
            if not dependPackage.scope: dependPackage.scope = parent.scope
            if parent.exclusions: dependPackage.exclusions += parent.exclusions

        # Add the default scope, if missing.
        if not dependPackage.scope:
          dependPackage.scope = Dict.Scopes.default

        # If the package definition is OK and affects processed scopes add it to the returned list.
        if ignoreScopes or dependPackage.scope in scopes:
          if dependPackage:
            depDest.append(dependPackage)
          else:
            raise AttaError(None, 'Incomplete package: %s' % str(dependPackage))

      return depDest

    # Handle <dependencyManagement> section.
    dmDep = pom.findall('dependencyManagement/dependencies/dependency')
    dmDependencies += _PreparePackagesFromDependencies(dmDep, True)

    # Handle <dependencies> section.
    dep = pom.findall('dependencies/dependency')
    dependencies += _PreparePackagesFromDependencies(dep)

    # Handle top level <packaging> section.
    packaging = pom.values(Dict.packaging)
    if len(packaging) > 0:
      package.type = packaging[0][Dict.packaging]

    if logFn: logFn(Dict.msgCollectingDependenciesForX % package.AsStr(), level = LogLevel.DEBUG)
    return dependencies, dmDependencies

  @staticmethod
  def GetDependenciesFromPOM(package, pom, scopes, includeOptional = False, logFn = None):
    props = Repository.GetPropertiesFromPOM(package, pom, logFn)
    dependencies, dmDependencies = Repository._GetDependenciesFromPOM(package, pom, props, scopes, includeOptional, logFn)
    return dependencies

  #
  # Others

  def _Name(self):
#    name = Task._Name(self)
#    return 'Maven.' + name
    return 'Maven'
