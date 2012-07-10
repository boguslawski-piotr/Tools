'''.. no-user-reference:'''
from ..tools import OS
from .. import Dict

class PackageId:
  '''TODO: description'''
  def __init__(self, groupId = None, artifactId = None, version = None, type = None, **tparams):
    self.groupId = groupId
    self.artifactId = artifactId
    if self.groupId is None:
      self.groupId = self.artifactId
    self.version = version
    self.type = type
    self.timestamp = tparams.get('timestamp')
    
    #self.scope
    #self.optional
    #self.exclusions
    
  def __eq__(self, other):
    return str(self) == str(other)
  
  def __cmp__(self, other):
    raise RuntimeError("PackageId objects can be compared only to the fact equality.")
  
  def __nonzero__(self):
    return self.groupId is not None and self.artifactId is not None and self.version is not None and self.type is not None
  def __bool__(self):
    return self.__nonzero__()
  
  def __str__(self):
    '''TODO: description'''
    return self.AsStr()
  
  def AsStr(self):
    '''TODO: description'''
    if self.groupId is None or self.groupId == self.artifactId:
      return '%s.%s:%s' % (str(self.artifactId), str(self.type), str(self.version))
    else: 
      return '%s:%s.%s:%s' % (str(self.groupId), str(self.artifactId), str(self.type), str(self.version))

  def AsStrWithoutType(self):
    '''TODO: description'''
    if self.groupId is None or self.groupId == self.artifactId:
      return '%s:%s' % (str(self.artifactId), str(self.version))
    else: 
      return '%s:%s:%s' % (str(self.groupId), str(self.artifactId), str(self.version))
  
  def AsDependencyInPOM(self):
    xml = Dict.dependencyStartTag + Dict.newLine
    
    def OneLine(n, v):
      if not v:
        return ''
      return '<' + n + '>' + v + '</' + n + '>' + Dict.newLine
    
    xml = xml + OneLine(Dict.groupId, self.groupId)    
    xml = xml + OneLine(Dict.artifactId, self.artifactId)    
    xml = xml + OneLine(Dict.version, self.version)    
    xml = xml + OneLine(Dict.type, self.type)    
    
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
  
  def IsOptional(self):
    '''TODO: description'''
    optional = getattr(self, Dict.optional, False)
    if not optional:
      return False
    if isinstance(optional, basestring):
      optional = optional.lower().strip()
      if optional == Dict.true or optional == Dict.yes:
        return True
      return False
    else:
      return bool(optional)
    
  def Excludes(self, packageId):
    '''Checks if `packageId` is on the `exclusions` list
       that is created when you download the dependencies
       from POM files.''' 
    excludedPackages = getattr(self, Dict.exclusions, [])
    for e in excludedPackages:
      if packageId.groupId == e.groupId and packageId.artifactId == e.artifactId:
        return True
    return False
     
  @staticmethod
  def FromStr(packageStrId):
    '''TODO: description'''
    groupId = artifactId = type = version = None
    try:
      items = packageStrId.split(':')
      if len(items) >= 3:
        groupId = items[0]
        del items[0]
      artifactId = OS.Path.RemoveExt(items[0])
      type = OS.Path.Ext(items[0])
      version = items[1]
    except:
      pass
    return PackageId(groupId, artifactId, version, type)

  @staticmethod
  def __Override(packageId, **tparams):
    if Dict.groupId in tparams: packageId.groupId = tparams.get(Dict.groupId)
    if Dict.artifactId in tparams: packageId.artifactId = tparams.get(Dict.artifactId)
    if Dict.version in tparams: packageId.version = tparams.get(Dict.version)
    if Dict.type in tparams: packageId.type = tparams.get(Dict.type)
    if packageId.groupId is None:
      packageId.groupId = packageId.artifactId
    return packageId

  @staticmethod
  def FromPackageId(packageId, **tparams):
    '''TODO: description'''
    newPackageId = PackageId.FromStr(str(packageId))
    return PackageId.__Override(newPackageId, **tparams)
    
  @staticmethod
  def FromDict(packageDict, **tparams):
    '''TODO: description'''
    newPackageId = PackageId.FromStr('')
    for e in packageDict:
      setattr(newPackageId, Dict.type if e == Dict.packaging else e, packageDict[e])
    return PackageId.__Override(newPackageId, **tparams)
        