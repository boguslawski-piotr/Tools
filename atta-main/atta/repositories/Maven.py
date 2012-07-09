'''.. Remote: TODO'''
import urllib2
import json
import cStringIO

from ..tools import DefaultVarsExpander
from ..tools.Misc import NamedFileLike, LogLevel, strip
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
     returns list (of strings: fileName) of localy available files
  '''
  def Get(self, packageId, scope, store = None):
    '''TODO: description'''
    self._DumpParams(locals())
    if not packageId:
      raise AttaError(self, Dict.errNotEnoughParams)
    
    if store is None:
      from . import Local
      store = Local.Repository({Dict.style : Styles.Maven}) 
    if store is None:
      raise AttaError(self, Dict.errNotSpecified.format(Dict.putIn))

    filesInStore = store.Check(packageId, scope)
    if filesInStore is None:
      # Get artifact information.
      self.Log('Fetching information for: ' + str(packageId), level = LogLevel.INFO)
      packageId.timestamp = Repository.GetArtifactTimestamp(packageId, self.Log)
      if packageId.timestamp is not None:
        filesInStore = store.Check(packageId, scope)
          
      if filesInStore is None:
        # Get the dependencies.
        filesInStore = []
        pom = None
        pomFile = Repository.GetArtifactPOMFile(packageId, self.Log)
        if pomFile:
          pom = pomFile.read()
        if pom:
          packages = Repository.GetDependenciesFromPOM(packageId, pom, Dict.Scopes.map2POM.get(scope, []), logFn = self.Log)
          for p in packages:
            filesInStore += self.Get(p, scope, store)
      
        # Get artifact.
        self.Log('Downloading: %s to: %s' % (packageId, store._Name()), level = LogLevel.INFO)
        filesToDownload = []
        if packageId.type != Dict.pom or not pom:
          try:
            f = Repository.GetArtifactFile(packageId, pom, self.Log)
            filesToDownload.append(NamedFileLike(Styles.Maven().FileName(packageId), f))
          except urllib2.HTTPError as E:
            if E.code == 404: pass
            else: raise
        if pom:
          filesToDownload.append(
            NamedFileLike(Styles.Maven().FileName(PackageId.FromPackageId(packageId, type = Dict.pom)), cStringIO.StringIO(pom)))
        try:
          if len(filesToDownload) > 0:
            filesInStore += store.Put(filesToDownload, '', packageId)
        finally:
          for i in range(len(filesToDownload)):
            filesToDownload[i] = None 
          
      else:
        self.Log('Up to date.', level = LogLevel.VERBOSE)
      
    if filesInStore is None or len(filesInStore) <= 0:
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    
    self.Log('Returns: %s' % OS.Path.FromList(filesInStore), level = LogLevel.VERBOSE)
    return filesInStore

  def Check(self, packageId, scope):
    raise AttaError(self, Dict.errNotImplemented.format('Check'))
  
  def Put(self, f, fBaseDirName, packageId):
    raise AttaError(self, Dict.errNotImplemented.format('Put'))

  @staticmethod
  def GetArtifactTimestamp(packageId, logFn = None):
    '''TODO: description'''
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % (packageId.groupId, packageId.artifactId, packageId.version, packageId.type)
    if logFn != None:
      logFn('From: %s' % url, level = LogLevel.DEBUG)
    f = urllib2.urlopen(url)
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
    url = Repository.GetArtifactUrlFromPOM(pom, logFn)
    if url == None:
      url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(packageId.groupId.replace('.', '/'), packageId.artifactId, packageId.version, packageId.type)
    if logFn != None:
      logFn('From: %s' % url, level = LogLevel.DEBUG)
    return urllib2.urlopen(url)

  @staticmethod
  def GetArtifactPOMFile(packageId, logFn = None):
    '''TODO: description'''
    try:
      return Repository.GetArtifactFile(PackageId.FromPackageId(packageId, type = Dict.pom), None, logFn)
    except urllib2.HTTPError as E:
      if E.code == 404: return None
      else: raise
  
  @staticmethod
  def GetArtifactUrlFromPOM(pom, logFn = None):
    '''TODO: description'''
    # TODO: handle this (?):
    '''
<relocation>
      <groupId>org.apache</groupId>
      <artifactId>my-project</artifactId>
      <version>1.0</version>
      <message>We have moved the Project under Apache</message>
</relocation>
'''          
    if pom != None:
      if not isinstance(pom, Xml):
        pom = Xml(pom)
      url = pom.values('distributionManagement/downloadUrl', stripfn = strip)
      if len(url) > 0:
        return url[0]['downloadUrl']
    return None
  
  @staticmethod
  def __GetPOM(packageId, pom):  
    # TODO: napisac jakos porzadniej
    getPOMFn = Repository.GetArtifactPOMFile
    if pom != None and '__call__' in dir(pom):
      getPOMFn = pom
      pom = getPOMFn(packageId)
      if pom == None:
        getPOMFn = Repository.GetArtifactPOMFile
        pom = getPOMFn(packageId)
    
    return (getPOMFn, pom)
  
  @staticmethod
  def _GetPropertiesFromPOM(packageId, pom, logFn = None):
    getPOMFn, pom = Repository.__GetPOM(packageId, pom)    
    if pom == None:
      return []
    
    if not isinstance(pom, Xml):
      pom = Xml(pom)
    
    props = []
    parent = pom.values(Dict.parent, stripfn = strip)
    if len(parent) > 0:
      for p in parent:
        #print p
        if not Dict.relativePath in p:
          parentPackageId = PackageId.FromDict(p, type = Dict.pom)
          props += Repository._GetPropertiesFromPOM(parentPackageId, getPOMFn, logFn)
          if logFn != None:
            logFn(Dict.msgGettingProperties % str(parentPackageId), level = LogLevel.VERBOSE)
    
    props += pom.values(Dict.properties, stripfn = strip)
    
    def _ProjectProps(name):
      p = pom.values(name, stripfn = strip)
      if p:
        p[0][Dict.project + '.' + name] = p[0][name]
      return p
    props += _ProjectProps(Dict.groupId)
    props += _ProjectProps(Dict.artifactId)
    props += _ProjectProps(Dict.packaging)
    props += _ProjectProps(Dict.version)
    
    return props

  @staticmethod
  def GetPropertiesFromPOM(packageId, pom, logFn = None):
    '''TODO: description'''
    props = Repository._GetPropertiesFromPOM(packageId, pom, logFn)
    d = {}
    for p in props:
      d.update(p)
    if logFn != None:
      logFn(Dict.msgGettingProperties % str(PackageId.FromDict(d, type = Dict.pom)), level = LogLevel.VERBOSE)
    return d
  
  @staticmethod
  def GetDependenciesFromPOM(packageId, pom, scopes, includeOptional = False, logFn = None):
    '''TODO: description'''
    assert scopes != None
    assert isinstance(scopes, list)
    
    # TODO: format moze byc jeszcze taki jak ponizej, czy to obslugiwac?
    '''
    <dependencyManagement>
      <dependencies>
      ...
      </dependencies>
    </dependencyManagement>
    '''
    
    getPOMFn, pom = Repository.__GetPOM(packageId, pom)    
    if pom == None:
      return []
    if not isinstance(pom, Xml):
      pom = Xml(pom)
    
    dependencies = []
    
    parent = pom.values(Dict.parent, stripfn = strip)
    if len(parent) > 0:
      for p in parent:
        if not Dict.relativePath in p:
          parentPackageId = PackageId.FromDict(p, type = Dict.pom)
          dependencies += Repository.GetDependenciesFromPOM(parentPackageId, getPOMFn, scopes, includeOptional, logFn)
          dependencies += [parentPackageId]
          
    props = Repository.GetPropertiesFromPOM(packageId, getPOMFn, logFn)
    expander = DefaultVarsExpander.Expander()
    dep = pom.findall('dependencies/dependency')
    for d in dep:
      dependPackageId = PackageId(type = 'jar')
      dependPackageId.scope = Dict.Scopes.compile
      for i in list(d):
        ltag = i.tag.lower()
        if ltag == Dict.exclusions:
          pass # TODO: handle it!
        else:
          if not includeOptional:
            if ltag == Dict.optional:
              if i.text.lower().strip() == Dict.true:
                dependPackageId = None
                break
          text = expander.Expand(i.text, **props)
          setattr(dependPackageId, i.tag, text)

      # TODO: co zrobic gdy brak version?
      # teraz sie po prostu nie zalapie, ale moze trzeba szukac wersji najnowszej?
       
      if dependPackageId:
        if dependPackageId.scope in scopes:
          dependencies.append(dependPackageId)
            
    packaging = pom.values(Dict.packaging)
    if len(packaging) > 0:
      packageId.type = packaging[0][Dict.packaging]
      
    return dependencies

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name
