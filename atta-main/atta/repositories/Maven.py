""".. Remote: TODO"""
import urllib2
import json
import cStringIO

from ..tools import DefaultVarsExpander
from ..tools.Misc import NamedFileLike, RemoveDuplicates, strip
from .. import AttaError, Dict, LogLevel, OS, Xml, Task, PackageId
from .Base import ARepository
from . import ArtifactNotFoundError
from . import Styles

class Repository(ARepository, Task):
  """TODO: description
  """

  # TODO: handle this (?):
  #<relocation>
  #      <groupId>org.apache</groupId>
  #      <artifactId>my-project</artifactId>
  #      <version>1.0</version>
  #      <message>We have moved the Project under Apache</message>
  #</relocation>

  def _Get(self, package, scope, store, resolvedPackages):
    #self._DumpParams(locals())

    # Check parameters.
    if not bool(package.type):
      package.type = Dict.jar
    if not package:
      raise AttaError(self, Dict.errNotEnoughParams)

    if store is None:
      from . import Local
      store = Local.Repository({Dict.style : Styles.Maven})
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))

    # First, see in store (cache) if the required files (for package and its dependencies) are all up to date.
    store.SetOptionalAllowed(self.OptionalAllowed())
    filesInStore = store.Check(package, scope)
    if filesInStore is None:
      # If something is obsolete then get detailed information
      # about the package and check store (cache) again.
      package.timestamp = Repository.GetArtifactTimestamp(package, self.Log)
      if package.timestamp is not None:
        filesInStore = store.Check(package, scope)

      if filesInStore is None:
        # Store still says that something is missing or out of date.
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
          if len(packages) > 0:
            # After downloading all the dependencies, check the store third time.
            # This is intended to minimize the amount of downloads.
            filesInStore2 = store.Check(package, scope)
            if filesInStore2:
              download = False
              filesInStore = filesInStore2

        # Get the artifact.
        if download:
          self.Log(Dict.msgSendingXToY % (package.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
          filesToDownload = []
          if package.type != Dict.pom or not pom:
            f = Repository.GetArtifactFile(package, pom, self.Log)
            if f is not None:
              filesToDownload.append(NamedFileLike(Styles.Maven().FileName(package), f))
          if pom:
            filesToDownload.append(
              NamedFileLike(Styles.Maven().FileName(PackageId.FromPackage(package, type = Dict.pom)), cStringIO.StringIO(pom)))
          try:
            if len(filesToDownload) > 0:
              filesInStore += store.Put('', filesToDownload, package)
          finally:
            for i in range(len(filesToDownload)):
              filesToDownload[i] = None

    # Check the results.
    if not package.optional:
      if filesInStore is None or len(filesInStore) <= 0:
        raise ArtifactNotFoundError(self, "Can't find: " + str(package))

    # Return the package files and its dependencies files.
    filesInStore = RemoveDuplicates(filesInStore)
    self.Log(Dict.msgReturns % OS.Path.FromList(filesInStore), level = LogLevel.DEBUG)
    return filesInStore

  def Get(self, package, scope, store = None):
    """TODO: description
     returns list (of strings: fileName) of locally available files
    """
    return self._Get(package, scope, store, [])

  def Check(self, package, scope):
    raise AttaError(self, Dict.errNotImplemented.format('Check'))

  def Put(self, fBaseDirName, files, package):
    raise AttaError(self, Dict.errNotImplemented.format('Put'))

  @staticmethod
  def GetArtifactTimestamp(package, logFn = None):
    """TODO: description"""
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % \
                                                        (package.groupId, package.artifactId, package.version, package.type)
    if logFn: logFn('Getting timestamp for: %s from: %s' % (str(package), url), level = LogLevel.VERBOSE)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError as E:
      if E.code == 404:
        if logFn: logFn(Dict.errXWhileGettingTimestamp, level = LogLevel.VERBOSE)
        return None
      raise

    jsonData = json.load(f)
    response = jsonData.get('response')
    timestamp = None
    if response:
      docs = response.get('docs')
      if docs and len(docs) > 0:
        timestamp = docs[0]['timestamp']
    return timestamp

  @staticmethod
  def GetArtifactFile(package, pom = None, logFn = None):
    """TODO: description"""
    # Try to download the file from the repository 'Maven Central'.
    url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(
                          package.groupId.replace('.', '/'), package.artifactId, package.version, package.type)
    if logFn:
      logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
    try:
      return urllib2.urlopen(url)
    except urllib2.HTTPError as E:
      if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(package), url), level = LogLevel.ERROR)
      if pom:
        # When the error occurred, check the alternate place from which you can download the file.
        # If it is specified in the POM file.
        url = Repository.GetArtifactUrlFromPOM(pom, logFn)
        if url:
          if logFn: logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
          try:
            return urllib2.urlopen(url)
          except urllib2.HTTPError as E:
            if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(package), url), level = LogLevel.ERROR)
    return None

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
                                 Repository.GetArtifactFile(package, None, logFn), logFn)
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
      url = pom.values('distributionManagement/downloadUrl', stripfn = strip)
      if len(url) > 0:
        return url[0]['downloadUrl']
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
      return []
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

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name
