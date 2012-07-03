'''.. Remote: TODO'''
import urllib2
import json
import re
import xml.etree.ElementTree
import cStringIO

from atta import AttaError, LogLevel, Task, Dictionary
from ..tools.Misc import NamedFileLike
from Base import ARepository
from . import ArtifactNotFoundError
from Package import PackageId
import Styles
import Local
import atta.tools.OS as OS
import atta.Dictionary as Dictionary
  
class Repository(ARepository, Task):
  '''TODO: description
     returns list (of strings: fileName) of localy available files
  '''
  def Get(self, packageId, scope, store = None):
    '''TODO: description'''
    self._DumpParams(locals())
    if not packageId:
      raise AttaError(self, Dictionary.errNotEnoughParams)
    
    if store is None:
      store = Local.Repository({Dictionary.style : Styles.Maven}) 
    if store is None:
      raise AttaError(self, Dictionary.errNotSpecified.format(Dictionary.putIn))

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
        pom = Repository.GetArtifactPOMContents(packageId)
        if pom:
          packages = Repository.GetDependenciesFromPOM(pom, Dictionary.Scopes.map2POM.get(scope, []))
          for p in packages:
            #new = Repository(self.data)
            #filesInStore += new.Get(p, scope, store)
            filesInStore += self.Get(p, scope, store)
      
        # Get artifact.
        self.Log('Downloading: %s to: %s' % (packageId, store._Name()), level = LogLevel.INFO)
        filesToDownload = [NamedFileLike(Styles.Maven().FileName(packageId), Repository.GetArtifactFile(packageId, pom, self.Log))]
        if pom:
          filesToDownload.append(
            NamedFileLike(Styles.Maven().FileName(PackageId.FromPackageId(packageId, type_ = Dictionary.pom)), cStringIO.StringIO(pom)))
        try:
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

  @staticmethod
  def GetArtifactTimestamp(packageId, logFn = None):
    '''TODO: description'''
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % (packageId.groupId, packageId.artifactId, packageId.version, packageId.type_)
    if logFn != None:
      logFn('From: %s' % url, level = LogLevel.DEBUG)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError as E:
      raise RuntimeError('%s\n%s' % (E.__str__(), url))
    else:
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
    url = Repository.GetArtifactUrlFromPOM(pom)
    if url == None:
      url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(packageId.groupId.replace('.', '/'), packageId.artifactId, packageId.version, packageId.type_)
    if logFn != None:
      logFn('From: %s' % url, level = LogLevel.DEBUG)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError as E:
      raise RuntimeError('%s\n%s' % (E.__str__(), url))
    else:
      return f

  @staticmethod
  def GetArtifactPOMFile(packageId):
    return Repository.GetArtifactFile(PackageId.FromPackageId(packageId, type_ = Dictionary.pom), None)
  
  @staticmethod
  def GetArtifactPOMContents(packageId):
    f = Repository.GetArtifactPOMFile(packageId)
    return f.read()
  
  @staticmethod
  def GetArtifactUrlFromPOM(pom):
    # TODO: handle this (?):
    '''
<relocation>
      <groupId>org.apache</groupId>
      <artifactId>my-project</artifactId>
      <version>1.0</version>
      <message>We have moved the Project under Apache</message>
</relocation>
'''          
    if pom == None:
      return None
    pom = xml.etree.ElementTree.fromstring(pom)
    for e in list(pom):
      if 'distributionmanagement' in e.tag.lower():
        for d in list(e):
          tag = d.tag; ltag = tag.lower()
          if 'downloadurl' in ltag:
            return d.text.strip()
    return None
  
  @staticmethod
  def GetDependenciesFromPOM(pom, scopes, includeOptional = False):
    def _RemoveNS(tag):
      ns = re.search('({.*})', tag)
      if ns != None: 
        tag = tag.replace(ns.group(1), '')
      return tag
    
    assert scopes != None
    assert isinstance(scopes, list)
    
    # TODO: handle <properties>
    # TODO: handle: <parent> (? czy aby na pewno)
    # TODO: format moze byc jeszcze taki:
    '''
    <dependencyManagement>
      <dependencies>
      ...
      </dependencies>
    </dependencyManagement>
    '''
    
    pom = xml.etree.ElementTree.fromstring(pom)
    dependencies = []
    for e in list(pom):
      if Dictionary.dependencies in e.tag:
        for d in list(e):
          packageId = PackageId(type_ = 'jar')
          packageId.scope = Dictionary.Scopes.compile
          for i in list(d):
            tag  = _RemoveNS(i.tag)
            ltag = tag.lower()
            if ltag == Dictionary.exclusions:
              pass # TODO: handle it!
            else:
              if not includeOptional:
                if ltag == Dictionary.optional:
                  if i.text.lower().strip() == Dictionary.true:
                    packageId = None
                    break
              setattr(packageId, tag, i.text)

          # TODO: co zrobic gdy brak version?
          # teraz sie po prostu nie zalapie, ale moze trzeba szukac wersji najnowszej?
           
          if packageId:
            if packageId.scope in scopes:
              dependencies.append(packageId)
            
    return dependencies

  def Check(self, packageId, scope):
    raise AttaError(self, Dictionary.errNotImplemented.format('Check'))
  
  def Put(self, f, fBaseDirName, packageId):
    raise AttaError(self, Dictionary.errNotImplemented.format('Put'))

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name
