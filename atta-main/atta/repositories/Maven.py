'''.. Remote: TODO'''
import urllib2
import json

from atta import Atta, AttaError, LogLevel, Task
from Base import ARepository
from . import ArtifactNotFoundError
import atta.tools.OS as OS
  
class Repository(ARepository, Task):
  '''TODO: description
     returns list (of strings: fileName) of localy available files
  '''

  def Get(self, packageId, store = None):
    '''TODO: description'''
    self._DumpParams(locals())
    
    if store is None or not packageId:
      raise AttaError(self, 'Not enough parameters.')

    # TODO: Is Maven has stored in the package it's dependencies?
    # If so, we also need them to load properly.
    
    filesInStore = store.Check(packageId)
    if filesInStore is None:
      # get artifact information
      self.Log('Fetching information for: ' + str(packageId), level = LogLevel.INFO)
      packageId.timestamp = self.GetTimestamp(packageId)
      if packageId.timestamp is not None:
        filesInStore = store.Check(packageId)
          
      if filesInStore is None:
        # get artifact
        self.Log('Downloading: %s to: %s' % (packageId, store._Name()), level = LogLevel.INFO)
        f = self.GetFile(packageId)
        try:
          filesInStore = store.Put(f, '', packageId)
        finally:
          f.close()
      else:
        self.Log('Up to date.', level = LogLevel.VERBOSE)
      
    if filesInStore is None or len(filesInStore) <= 0:
      raise ArtifactNotFoundError(self, "Can't find: " + str(packageId))
    
    self.Log('Returns: %s' % OS.Path.FromList(filesInStore), level = LogLevel.VERBOSE)
    return filesInStore

  def GetTimestamp(self, packageId):
    '''TODO: description'''
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % (packageId.groupId, packageId.artifactId, packageId.version, packageId.type_)
    self.Log('From: %s' % url, level = LogLevel.DEBUG)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
      raise AttaError(self, '%s\n%s' % (url, e.__str__()))
    else:
      jsonData = json.load(f)
      response = jsonData.get('response')
      timestamp = None
      if response is not None:
        docs = response.get('docs')
        if docs is not None and len(docs) > 0:
          timestamp = docs[0]['timestamp']
      return timestamp
  
  def GetFile(self, packageId):
    '''TODO: description'''
    url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(packageId.groupId.replace('.', '/'), packageId.artifactId, packageId.version, packageId.type_)
    self.Log('From: %s' % url, level = LogLevel.DEBUG)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
      raise AttaError(self, '%s\n%s' % (url, e.__str__()))
    else:
      return f

  def Check(self, packageId):
    raise AttaError(self, 'Not implemented: Check')
  
  def Put(self, f, fBaseDirName, packageId):
    raise AttaError(self, 'Not implemented: Put')

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name

