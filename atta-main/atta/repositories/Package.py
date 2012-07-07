'''.. no-user-reference:'''
from ..tools import OS
from .. import Dict

class PackageId:
  '''TODO: description'''
  def __init__(self, groupId = None, artifactId = None, version = None, type_ = None, **tparams):
    self.groupId = groupId
    self.artifactId = artifactId
    if self.groupId is None:
      self.groupId = self.artifactId
    self.version = version
    self.type_ = type_
    self.timestamp = tparams.get('timestamp')
    
  def __eq__(self, other):
    return str(self) == str(other)
  
  def __cmp__(self, other):
    raise RuntimeError("PackageId objects can be compared only to the fact equality.")
  
  def __nonzero__(self):
    return self.groupId is not None and self.artifactId is not None and self.version is not None and self.type_ is not None
  
  def __str__(self):
    '''TODO: description'''
    return self.AsStr(self)
  
  def AsStr(self, packageId):
    '''TODO: description'''
    if packageId.groupId is None or packageId.groupId == packageId.artifactId:
      return '%s.%s:%s' % (str(packageId.artifactId), str(packageId.type_), str(packageId.version))
    else: 
      return '%s:%s.%s:%s' % (str(packageId.groupId), str(packageId.artifactId), str(packageId.type_), str(packageId.version))
  
  def AsDependencyInPOM(self):
    xml = Dict.dependencyStartTag + Dict.newLine
    
    def OneLine(n, v):
      if not v:
        return ''
      return '<' + n + '>' + v + '</' + n + '>' + Dict.newLine
    
    xml = xml + OneLine(Dict.groupId, self.groupId)    
    xml = xml + OneLine(Dict.artifactId, self.artifactId)    
    xml = xml + OneLine(Dict.version, self.version)    
    xml = xml + OneLine(Dict.type, self.type_)    
    
    if Dict.systemPath in dir(self):
      xml = xml + OneLine(Dict.systemPath, self.systemPath)    
    if Dict.scope in dir(self):
      scopes = Dict.Scopes.map2POM.get(self.scope, [])
      if len(scopes) > 0:
        scope = scopes[len(scopes)-1]
      else:
        scope = self.scope
      xml = xml + OneLine(Dict.scope, scope)    
          
    xml = xml + Dict.dependencyEndTag + Dict.newLine
    return xml
  
  @staticmethod
  def FromStr(packageStrId):
    '''TODO: description'''
    groupId = artifactId = type_ = version = None
    try:
      items = packageStrId.split(':')
      if len(items) >= 3:
        groupId = items[0]
        del items[0]
      artifactId = OS.Path.RemoveExt(items[0])
      type_ = OS.Path.Ext(items[0])
      version = items[1]
    except:
      pass
    return PackageId(groupId, artifactId, version, type_)

  @staticmethod
  def FromPackageId(packageId, groupId = None, artifactId = None, version = None, type_ = None, **tparams):
    newPackageId = PackageId.FromStr(str(packageId))
    if groupId != None: newPackageId.groupId = groupId
    if artifactId != None: newPackageId.artifactId = artifactId
    if version != None: newPackageId.version = version
    if type_ != None: newPackageId.type_ = type_
    return newPackageId
    