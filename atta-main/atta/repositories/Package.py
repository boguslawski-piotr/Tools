""".. no-user-reference:"""
from ..tools.internal.Misc import ObjectFromClass
from ..tools import OS
from .. import Dict

class PackageId:
  """TODO: description"""
  def __init__(self, groupId = None, artifactId = None, version = None, type = None, **tparams):
    self.groupId = groupId
    self.artifactId = artifactId
    if not self.groupId: self.groupId = self.artifactId
    self.version = version
    self.type = type
    if not self.type: self.type = None
    self.timestamp = tparams.get('timestamp')

    #self.scope
    #self.optional
    #self.exclusions
    #self.sha1?

  def GetAttr(self, name, default = None):
    """TODO: description"""
    return getattr(self, name, default)

  def SetAttr(self, name, value):
    """TODO: description"""
    setattr(self, name, value)

  def __setattr__(self, name, value):
    name = Dict.type if name == Dict.packaging else name
    self.__dict__[name] = value

  def IsOptional(self):
    """TODO: description"""
    optional = self.GetAttr(Dict.optional, False)
    if isinstance(optional, basestring):
      optional = optional.lower().strip()
      return optional == Dict.true or optional == Dict.yes
    else:
      return bool(optional)

  def Excludes(self, package):
    """Checks if *package* is on the *exclusions* list
       that is usually created when you download the dependencies
       from POM files."""
    excludedPackages = self.GetAttr(Dict.exclusions, [])
    for e in excludedPackages:
      if package.groupId == e.groupId and package.artifactId == e.artifactId:
        return True
    return False

  def AsStr(self):
    """TODO: description"""
    if not self.groupId or self.groupId == self.artifactId:
      return '%s.%s:%s' % (str(self.artifactId), str(self.type), str(self.version))
    else:
      return '%s:%s.%s:%s' % (str(self.groupId), str(self.artifactId), str(self.type), str(self.version))

  def AsStrWithoutType(self):
    """TODO: description"""
    if not self.groupId or self.groupId == self.artifactId:
      return '%s:%s' % (str(self.artifactId), str(self.version))
    else:
      return '%s:%s:%s' % (str(self.groupId), str(self.artifactId), str(self.version))

  def AsFileName(self, style):
    style = ObjectFromClass(style)
    return style.GetObject().FileName(self)

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
        scope = scopes[len(scopes) - 1]
      else:
        scope = self.scope
      xml = xml + OneLine(Dict.scope, scope)
    if self.IsOptional():
      xml = xml + OneLine(Dict.optional, Dict.true)

    xml = xml + Dict.dependencyEndTag + Dict.newLine
    return xml

  @staticmethod
  def FromStr(packageStrId):
    """TODO: description"""
    groupId = artifactId = type = version = None
    try:
      items = packageStrId.split(':')
      if len(items) >= 3:
        groupId = items[0]
        del items[0]
      artifactId = OS.Path.RemoveExt(items[0])
      type = OS.Path.Ext(items[0])
      if type.lower() == 'none': type = None
      version = items[1]
    except:
      pass
    return PackageId(groupId, artifactId, version, type)

  @staticmethod
  def __Override(package, **tparams):
    if Dict.groupId in tparams: package.groupId = tparams.get(Dict.groupId)
    if Dict.artifactId in tparams: package.artifactId = tparams.get(Dict.artifactId)
    if not package.groupId: package.groupId = package.artifactId
    if Dict.version in tparams: package.version = tparams.get(Dict.version)
    if Dict.type in tparams: package.type = tparams.get(Dict.type)
    return package

  @staticmethod
  def FromPackage(package, **tparams):
    """TODO: description"""
    newPackage = PackageId.FromStr(str(package))
    return PackageId.__Override(newPackage, **tparams)

  @staticmethod
  def FromDict(packageData, **tparams):
    """TODO: description"""
    newPackage = PackageId()
    for name in packageData:
      setattr(newPackage, name, packageData[name])
    return PackageId.__Override(newPackage, **tparams)

  def __eq__(self, other):
    return str(self) == str(other)

  def __cmp__(self, other):
    raise RuntimeError("PackageId objects can be compared only to the fact equality.")

  def __nonzero__(self):
    return bool(self.groupId) and bool(self.artifactId) and bool(self.version) and bool(self.type)

  def __bool__(self):
    return self.__nonzero__()

  def __str__(self):
    """TODO: description"""
    return self.AsStr()
