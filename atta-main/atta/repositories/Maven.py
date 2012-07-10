'''.. Remote: TODO'''
import urllib2
import json
import cStringIO

from ..tools import DefaultVarsExpander
from ..tools.Misc import NamedFileLike, LogLevel, RemoveDuplicates, strip
from ..tools.Xml import Xml
from ..tools import OS
from ..tasks.Base import Task
from .. import AttaError
from .. import Dict
from .Base import ARepository
from .Package import PackageId
from . import ArtifactNotFoundError
from . import Styles

class Repository(ARepository, Task):
  '''TODO: description
  '''

  # TODO: handle this (?):
  '''
<relocation>
      <groupId>org.apache</groupId>
      <artifactId>my-project</artifactId>
      <version>1.0</version>
      <message>We have moved the Project under Apache</message>
</relocation>
'''

  def _Get(self, packageId, scope, store, resolvedPackages):
    # Check parameters.
    self._DumpParams(locals())
    if not packageId:
      raise AttaError(self, Dict.errNotEnoughParams)
    if store is None:
      from . import Local
      store = Local.Repository({Dict.style : Styles.Maven})
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))

    # First, see in store (cache) if the required files (for package and its dependencies) are all up to date.
    store.SetOptionalAllowed(self.OptionalAllowed())
    filesInStore = store.Check(packageId, scope)
    if filesInStore is None:
      # If something is obsolete then get detailed information 
      # about the package and check store (cache) again.
      packageId.timestamp = Repository.GetArtifactTimestamp(packageId, self.Log)
      if packageId.timestamp is not None:
        filesInStore = store.Check(packageId, scope)

      if filesInStore is None:
        # Store still says that something is missing or out of date.
        download = True
        filesInStore = []

        # Get the dependencies.
        pom = Repository.GetPOM(packageId, self.Log)
        if pom:
          packages = Repository.GetDependenciesFromPOM(
                        packageId, pom, Dict.Scopes.map2POM.get(scope, []), self.OptionalAllowed(), logFn = self.Log)
          for p in packages:
            if not packageId.Excludes(p):
              if p not in resolvedPackages:
                resolvedPackages.append(p)
                filesInStore += self._Get(p, scope, store, resolvedPackages)
          if len(packages) > 0:
            # After downloading all the dependencies, check the store third time.
            # This is intended to minimize the amount of downloads.
            filesInStore2 = store.Check(packageId, scope)
            if filesInStore2:
              download = False
              filesInStore = filesInStore2

        # Get artifact.
        if download:
          self.Log(Dict.msgSendingXToY % (packageId.AsStrWithoutType(), store._Name()), level = LogLevel.INFO)
          filesToDownload = []
          if packageId.type != Dict.pom or not pom:
            f = Repository.GetArtifactFile(packageId, pom, self.Log)
            if f != None:
              filesToDownload.append(NamedFileLike(Styles.Maven().FileName(packageId), f))
          if pom:
            filesToDownload.append(
              NamedFileLike(Styles.Maven().FileName(PackageId.FromPackageId(packageId, type = Dict.pom)), cStringIO.StringIO(pom)))
          try:
            if len(filesToDownload) > 0:
              filesInStore += store.Put(filesToDownload, '', packageId)
          finally:
            for i in range(len(filesToDownload)):
              filesToDownload[i] = None

    # Check results.
    if not packageId.IsOptional():
      if filesInStore is None or len(filesInStore) <= 0:
        raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))

    # Return package and its dependencies files.
    filesInStore = RemoveDuplicates(filesInStore)
    self.Log(Dict.msgReturns % OS.Path.FromList(filesInStore), level = LogLevel.DEBUG)
    return filesInStore

  def Get(self, packageId, scope, store = None):
    '''TODO: description
     returns list (of strings: fileName) of localy available files
    '''
    return self._Get(packageId, scope, store, [])

  def Check(self, packageId, scope):
    raise AttaError(self, Dict.errNotImplemented.format('Check'))

  def Put(self, f, fBaseDirName, packageId):
    raise AttaError(self, Dict.errNotImplemented.format('Put'))

  @staticmethod
  def GetArtifactTimestamp(packageId, logFn = None):
    '''TODO: description'''
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % \
                                                        (packageId.groupId, packageId.artifactId, packageId.version, packageId.type)
    if logFn: logFn('Getting timestamp for: %s from: %s' % (str(packageId), url), level = LogLevel.VERBOSE)
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
    if response is not None:
      docs = response.get('docs')
      if docs is not None and len(docs) > 0:
        timestamp = docs[0]['timestamp']
    return timestamp

  @staticmethod
  def GetArtifactFile(packageId, pom = None, logFn = None):
    '''TODO: description'''
    # Try to download the file from the repository 'Maven Central'.
    url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(
                          packageId.groupId.replace('.', '/'), packageId.artifactId, packageId.version, packageId.type)
    if logFn:
      logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
    try:
      return urllib2.urlopen(url)
    except urllib2.HTTPError as E:
      if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(packageId), url), level = LogLevel.ERROR)
      if pom:
        # When the error occurred, check the alternate place from which you can download the file. 
        # If it is specified in the POM file.
        url = Repository.GetArtifactUrlFromPOM(pom, logFn)
        if url:
          if logFn: logFn(Dict.msgDownloadingFile % url, level = LogLevel.VERBOSE)
          try:
            return urllib2.urlopen(url)
          except urllib2.HTTPError as E:
            if logFn: logFn(Dict.errXWhileGettingYFromZ % (str(E), str(packageId), url), level = LogLevel.ERROR)
    return None

  '''POM support'''

  _pomCache = {}

  @staticmethod
  def GetPOMCacheKey(packageId):
    '''TODO: description'''
    return str(packageId)

  @staticmethod
  def GetPOMFromCache(packageId, logFn = None):
    '''TODO: description'''
    key = Repository.GetPOMCacheKey(packageId)
    if key in Repository._pomCache:
      if logFn != None:
        logFn('Getting: %s from cache.' % str(packageId), level = LogLevel.DEBUG)
      return Repository._pomCache[key]
    return None

  @staticmethod
  def PutPOMIntoCache(packageId, f, logFn = None):
    '''TODO: description'''
    key = Repository.GetPOMCacheKey(packageId)
    if f != None:
      if 'read' in dir(f):
        Repository._pomCache[key] = f.read()
      else:
        Repository._pomCache[key] = f

  @staticmethod
  def GetPOM(packageId, logFn = None):
    '''Gets the POM file from Maven Central Repository.
       The function uses the local impermanent cache.
       Returns the POM contents or None.'''
    packageId = PackageId.FromPackageId(packageId, type = Dict.pom)
    pomFile = Repository.GetPOMFromCache(packageId, logFn)
    if pomFile == None:
      Repository.PutPOMIntoCache(packageId,
                                 Repository.GetArtifactFile(packageId, None, logFn), logFn)
    return Repository.GetPOMFromCache(packageId, logFn)

  @staticmethod
  def GetPOMEx(packageId, pom, logFn = None):
    '''Checks if the `pom` is the method/function used to download contents of a POM file.
       If so, uses it and trying to retrieve data. If the download did not succeed then 
       try again using the Maven Central Repository.
       Returns a tuple (`function`, `pom`) where `function` is a function/method 
       which you can use to download next POM file and `pom` points to the contents of the file.'''
    getPOMFn = Repository.GetPOM
    if pom != None and '__call__' in dir(pom):
      getPOMFn = pom
      pom = getPOMFn(packageId, logFn = logFn)
      if pom == None and getPOMFn != Repository.GetPOM:
        getPOMFn = Repository.GetPOM
        pom = getPOMFn(packageId, logFn = logFn)

    return (getPOMFn, pom)

  @staticmethod
  def GetArtifactUrlFromPOM(pom, logFn = None):
    '''TODO: description'''
    if pom != None:
      if not isinstance(pom, Xml):
        pom = Xml(pom)
      url = pom.values('distributionManagement/downloadUrl', stripfn = strip)
      if len(url) > 0:
        return url[0]['downloadUrl']
    return None

  @staticmethod
  def _GetPropertiesFromPOM(packageId, pom, logFn = None):
    # Prepare POM contents.
    getPOMFn, pom = Repository.GetPOMEx(packageId, pom, logFn)
    if pom == None:
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
          parentPackageId = PackageId.FromDict(p, type = Dict.pom)
          props += Repository._GetPropertiesFromPOM(parentPackageId, getPOMFn, logFn)

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

    if logFn: logFn(Dict.msgLoadingPropertiesForX % packageId.AsStrWithoutType(), level = LogLevel.DEBUG)
    return props

  @staticmethod
  def GetPropertiesFromPOM(packageId, pom, logFn = None):
    '''TODO: description'''
    props = Repository._GetPropertiesFromPOM(packageId, pom, logFn)
    d = {}
    for p in props:
      d.update(p)
    return d

  @staticmethod
  def _GetDependenciesFromPOM(packageId, pom, props, scopes, includeOptional = False, logFn = None):
    '''TODO: description'''
    assert scopes != None
    assert isinstance(scopes, list)

    # Prepare POM contents.
    getPOMFn, pom = Repository.GetPOMEx(packageId, pom, logFn = logFn)
    if pom == None:
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
          parentPackageId = PackageId.FromDict(p, type = Dict.pom)
          parentDependencies, parentDmDependencies = Repository._GetDependenciesFromPOM(parentPackageId,
                                                                                          getPOMFn, props, scopes, includeOptional, logFn)
          dependencies += parentDependencies
          dependencies += [parentPackageId]
          dmDependencies += parentDmDependencies

    expander = DefaultVarsExpander.Expander()

    def _PreparePackagesFromDependencies(depSrc, ignoreScopes = False):
      depDest = []
      for d in depSrc:
        # Collect package information from <dependency> section.
        dependPackageId = PackageId(type = 'jar')
        for i in list(d):
          ltag = i.tag.lower()
          if ltag == Dict.exclusions:
            dependPackageId.exclusions = []
            for es in list(i):
              excludePackageId = PackageId()
              for e in list(es):
                text = expander.Expand(e.text, **props)
                setattr(excludePackageId, e.tag, text)
              dependPackageId.exclusions.append(excludePackageId)
          else:
            if not includeOptional:
              if ltag == Dict.optional:
                if i.text.lower().strip() == Dict.true:
                  dependPackageId = None
                  break
            text = expander.Expand(i.text, **props)
            setattr(dependPackageId, i.tag, text)

        if dependPackageId is None:
          continue

        # Search for the missing properties in the definitions from parents.
        for pd in reversed(dmDependencies):
          if pd.groupId == dependPackageId.groupId and pd.artifactId == dependPackageId.artifactId:
            if dependPackageId.version == None:
              if Dict.version in dir(pd):
                dependPackageId.version = pd.version
            if not Dict.scope in dir(dependPackageId) or dependPackageId.scope == None:
              if Dict.scope in dir(pd):
                dependPackageId.scope = pd.scope
            if Dict.exclusions in dir(pd):
              if not Dict.exclusions in dir(dependPackageId):
                dependPackageId.exclusions = []
              dependPackageId.exclusions += pd.exclusions

        # Add the default scope, if missing.
        if not Dict.scope in dir(dependPackageId):
          dependPackageId.scope = Dict.Scopes.compile

        # If the package definition is OK and affects processed scopes add it to the returned list.
        if ignoreScopes or dependPackageId.scope in scopes:
          if dependPackageId:
            depDest.append(dependPackageId)
          else:
            raise AttaError(None, 'Incomplete package: %s' % str(dependPackageId))

      return depDest

    # Handle <dependencyManagement> section.
    dmDep = pom.findall('dependencyManagement/dependencies/dependency')
    dmDependencies += _PreparePackagesFromDependencies(dmDep, True)
#    for z in dmDependencies:
#      print z

    # Handle <dependencies> section.
    dep = pom.findall('dependencies/dependency')
    dependencies += _PreparePackagesFromDependencies(dep)

    # Handle top level <packaging> section. 
    packaging = pom.values(Dict.packaging)
    if len(packaging) > 0:
      packageId.type = packaging[0][Dict.packaging]

    if logFn: logFn(Dict.msgCollectingDependenciesForX % packageId.AsStr(), level = LogLevel.DEBUG)
    return (dependencies, dmDependencies)

  @staticmethod
  def GetDependenciesFromPOM(packageId, pom, scopes, includeOptional = False, logFn = None):
    props = Repository.GetPropertiesFromPOM(packageId, pom, logFn)
    dependencies, dmDependencies = Repository._GetDependenciesFromPOM(packageId, pom, props, scopes, includeOptional, logFn)
    return dependencies

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name
