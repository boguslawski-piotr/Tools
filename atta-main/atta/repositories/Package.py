'''.. no-user-reference:'''
import atta.tools.OS as OS

class PackageId:
  '''TODO: description'''
  def __init__(self, groupId, artifactId, version, type_, **tparams):
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

