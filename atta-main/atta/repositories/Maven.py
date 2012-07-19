""".. Remote: TODO"""
import urllib2
import json
import cStringIO
import os

from ..tools import DefaultVarsExpander
from ..tools.Misc import NamedFileLike, RemoveDuplicates, strip
from .. import AttaError, Dict, LogLevel, OS, Xml, Task, PackageId
from . import ArtifactNotFoundError, Interfaces, Styles, Local

class Repository(Local.Repository, Task):
  """TODO: description
  """
  def _Get(self, package, scope, store, resolvedPackages):
    # Check parameters.
    if not bool(package.type):
      package.type = Dict.jar
    if not package:
      raise AttaError(self, Dict.errPackageNotComplete % str(package))

    # First, see in the store (cache) if the required files (for package and its dependencies) are all up to date.
    filesInStore = store.Check(package, scope)
    problem = False
    if filesInStore is None:
      # If something is obsolete then get detailed information
      # about the package and check the store (cache) again.
      package.stamp = Repository.GetArtifactStamp(package, store.PrepareFileName(package), self.Log)
      if package.stamp is not None:
        filesInStore = store.Check(package, scope)
      if filesInStore is None:
        # The store still says that something is missing or out of date.
        download = True
        filesInStore = []

        # Get the dependencies.
        pom = Repository.GetPOM(package, self.Log)
        if pom:
          packages = Repository.GetDependenciesFromPOM(
                        package, pom, Dict.Scopes.map2POM.get(scope, []), self.OptionalAllowed(), logFn = self.Log)
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
          filesToDownload = []
          if pom:
            filesToDownload.append(NamedFileLike(Styles.Maven().FileName(PackageId.FromPackage(package, type = Dict.pom)),
                                   cStringIO.StringIO(pom)))
          if package.type != Dict.pom or not pom:
            f = Repository.GetArtifactFile(package, pom, store.PrepareFileName(package), self.Log)
            if f is not None:
              filesToDownload.append(NamedFileLike(Styles.Maven().FileName(package), f))
            else:
              problem = True
          if not problem and filesToDownload:
            self.Log(Dict.msgSendingXToY % (package.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
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

  def Get(self, package, scope, store = None):
    """TODO: description
     returns list (of strings: fileName) of locally available files
    """
    if store is None:
      store = Repository(style = Styles.Maven)
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))
    store.SetOptionalAllowed(self.OptionalAllowed())
    return self._Get(package, scope, store, [])

  def CompleteFileName(self, fileName):
    return os.path.normpath(os.path.join(os.path.expanduser('~'), '.m2', fileName))

  def PutMarkerFile(self, fileName, fileSha1, package):
    Local.Repository.PutMarkerFile(self, fileName, fileSha1, package)
    self.PutFileContents(str(fileSha1), OS.Path.JoinExt(fileName, 'sha1'))

  #
  # Resolvers

  class Central(Interfaces.IPackageUrls):
    """TODO: description"""
    def __init__(self, baseUrl = 'http://search.maven.org/'):
      self.baseUrl = baseUrl
      if not self.baseUrl.endswith('/'):
        self.baseUrl += '/'

    def StampUrl(self, package):
      return OS.Path.JoinExt(self.PackageUrl(package), 'sha1')

    def PackagePath(self, package):
      return '{0}/{1}/{2}/{1}-{2}.{3}'.format(
        str(package.groupId).replace('.', '/'), package.artifactId, package.version, package.type)

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
  def GetArtifactStamp(package, excludedUrl = None, logFn = None):
    """TODO: description"""
    resolvers = Repository.resolvers
    f = None
    for resolver in resolvers:
      url = resolver.StampUrl(package)
      if url and (not excludedUrl or url.find(excludedUrl) < 0):
        if logFn: logFn('Getting stamp for: %s from: %s' % (str(package), url), level = LogLevel.VERBOSE)
        try:
          f = urllib2.urlopen(url)
          break
        except urllib2.URLError as E:
          if logFn: logFn(Dict.errXWhileGettingStamp % E, level = LogLevel.VERBOSE)
          f = None
          continue
    if f is not None:
      try:
        return f.read()
      except Exception as E:
        if logFn: logFn(Dict.errXWhileGettingStamp % E, level = LogLevel.VERBOSE)
    return None

  @staticmethod
  def GetArtifactFile(package, pom = None, excludedUrl = None, logFn = None):
    """TODO: description"""
    # Try to download the file from the repository(ies).
    resolvers = Repository.resolvers
    for resolver in resolvers:
      url = resolver.PackageUrl(package)
      if url and (not excludedUrl or url.find(excludedUrl) < 0):
        if logFn:
          logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
        try:
          return urllib2.urlopen(url)
        except urllib2.URLError as E:
          if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(package), url), level = LogLevel.ERROR)
          continue

    # If the package is not found in any repository or when the error occurred,
    # check the alternate place(s) from which you can download the file.

    def _AlternateDownload(url):
      if url:
        if logFn: logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
        try:
          return urllib2.urlopen(url)
        except urllib2.HTTPError as E:
          if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(package), url), level = LogLevel.ERROR)
      return None

    if pom:
      # If is specified in the POM file.
      f = _AlternateDownload(Repository.GetArtifactUrlFromPOM(pom, logFn))
      if f is not None:
        return f
    if package.downloadUrl:
      # If is specified in the package definition.
      if isinstance(package.downloadUrl, Interfaces.IPackageUrls):
        return _AlternateDownload(package.downloadUrl.PackageUrl(package))
      else:
        return _AlternateDownload(package.downloadUrl)

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
  def GetPOM(package, logFn = None):
    """Gets the POM file from Maven Central Repository.
       The function uses the local impermanent cache.
       Returns the POM contents or None."""
    package = PackageId.FromPackage(package, type = Dict.pom)
    pomFile = Repository.GetPOMFromCache(package, logFn)
    if pomFile is None:
      Repository.PutPOMIntoCache(package,
                                 Repository.GetArtifactFile(package, None, None, logFn), logFn)
    return Repository.GetPOMFromCache(package, logFn)

  @staticmethod
  def GetPOMEx(package, pom, logFn = None):
    """Checks if the *pom* is the callable used to download contents of a POM file.
       If so, uses it and trying to retrieve data. If the download did not succeed then
       try again using the Maven Central Repository.
       Returns a tuple (*function*, *pom*) where *function* is a callable
       which you can use to download next POM file and *pom* points to the
       contents of the file or is None."""
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
