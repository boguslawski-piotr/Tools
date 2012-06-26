import urllib2
import json

from atta import Atta, AttaError, LogLevel, Task
from ..Interfaces import IRepository
  
class Repository(IRepository, Task):
  '''TODO: description
     returns list (of strings: fileName) of localy available files
  '''

  def Get(self, groupId, artifactId, version, type, store = None, **tparams):
    '''TODO: description'''
    if Atta.logger.GetLevel() == LogLevel.DEBUG:
      self.Log('\n*** Get parameters:')
      self.Log('groupId: {0}'.format(groupId))
      self.Log('artifactId: {0}'.format(artifactId))
      self.Log('version: {0}'.format(version))
      self.Log('type: {0}'.format(type))
      self.Log('store: {0}'.format(store))
      self.LogIterable('tparams:', tparams.items())
      self.Log('')
    
    if store is None or artifactId is None or version is None or type is None:
      raise AttaError(self, 'Not enough parameters.')

    if groupId is None:
      groupId = artifactId
    
    artifactInfo = store.Check(groupId, artifactId, version, type, None, **tparams)
    if artifactInfo is None:
      # get artifact information
      self.Log('Fetching information for: ' + IRepository.DisplayName(groupId, artifactId, version, type), level = LogLevel.INFO)
      timestamp = self.GetTimestamp(groupId, artifactId, version, type, **tparams)
      if timestamp is not None:
        artifactInfo = store.Check(groupId, artifactId, version, type, timestamp = timestamp, **tparams)
          
      if artifactInfo is None:
        # get artifact
        self.Log('Downloading to: %s' % store._Name(), level = LogLevel.INFO)
        f = self.GetFile(groupId, artifactId, version, type, **tparams)
        try:
          artifactInfo = store.Put(f, timestamp, groupId, artifactId, version, type, **tparams)
        finally:
          f.close()
      else:
        self.Log('Up to date.', level = LogLevel.VERBOSE)
      
    if artifactInfo is None:
      raise AttaError(self, "Can't find: " + IRepository.DisplayName(groupId, artifactId, version, type))
    
    return [artifactInfo[0]]

  def GetTimestamp(self, groupId, artifactId, version, type, **tparams):
    '''TODO: description'''
    url = 'http://search.maven.org/solrsearch/select?q=g:"%s"+AND+a:"%s"+AND+v:"%s"+AND+p:"%s"&core=gav&rows=20&wt=json' % (groupId, artifactId, version, type)
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
  
  def GetFile(self, groupId, artifactId, version, type, **tparams):
    '''TODO: description'''
    url = 'http://search.maven.org/remotecontent?filepath={0}/{1}/{2}/{1}-{2}.{3}'.format(groupId.replace('.', '/'), artifactId, version, type)
    self.Log('From: %s' % url, level = LogLevel.DEBUG)
    try:
      f = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
      raise AttaError(self, '%s\n%s' % (url, e.__str__()))
    else:
      return f

  def Check(self, groupId, artifactId, version, type, timestamp, **tparams):
    raise AttaError(self, 'Not implemented: Check')
  
  def Put(self, f, timestamp, groupId, artifactId, version, type, **tparams):
    raise AttaError(self, 'Not implemented: Put')

  def _Name(self):
    name = Task._Name(self)
    return 'Maven.' + name

