""".. no-user-reference:"""
from ..tools.internal.Misc import ObjectFromClass
from ..tools.Misc import isstring
from .. import Dict, OS

class PackageId:
  """TODO: description"""
  def __init__(self, groupId = None, artifactId = None, version = None, type = None, **tparams):
    self.artifactId = artifactId
    self.groupId = groupId
    self.version = version
    self.type = type
    self.stamp = tparams.get('stamp')

    #self.scope
    #self.optional
    #self.exclusions
    #self.downloadUrl
    #self.fileNames

  def __getattr__(self, name):
    if name == Dict.exclusions:
      self.__dict__[name] = []
      return self.__dict__[name]
    else:
      return None

  def __setattr__(self, name, value):
    name = Dict.type if name == Dict.packaging else name

    if name == Dict.groupId:
      if not value:
        value = self.artifactId
    elif name == Dict.exclusions:
      values = OS.Path.AsList(value, ',')
      value = []
      for v in values:
        if isstring(v): v = PackageId.FromStr(v)
        elif isinstance(v, dict): v = PackageId.FromDict(v)
        value.append(v)
    elif name == Dict.optional:
      if isstring(value):
        value = value.lower().strip()
        value = value == Dict.true or value == Dict.yes
      else:
        value = bool(value)
    else:
      if not value:
        value = None

    self.__dict__[name] = value

  def Excludes(self, package):
    """Checks if *package* is on the *exclusions* list that is usually
       created when you download the dependencies from POM files."""
    for e in self.exclusions:
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
    """TODO: description"""
    style = ObjectFromClass(style)
    return style.GetObject().FileName(self)

  def AsFullFileName(self, style):
    """TODO: description"""
    style = ObjectFromClass(style)
    return style.GetObject().FullFileName(self)

  def AsDependencyInPOM(self):
    """TODO: description"""
    xml = Dict.dependencyStartTag + Dict.newLine

    def OneLine(n, v, s = 2):
      if not v:
        return ''
      return ' ' * s + '<' + n + '>' + v + '</' + n + '>' + Dict.newLine

    xml += OneLine(Dict.groupId, self.groupId)
    xml += OneLine(Dict.artifactId, self.artifactId)
    xml += OneLine(Dict.version, self.version)
    xml += OneLine(Dict.type, self.type)

    if self.systemPath:
      xml += OneLine(Dict.systemPath, self.systemPath)
    if self.scope:
      scopes = Dict.Scopes.map2POM.get(self.scope, [])
      if len(scopes) > 0:
        scope = scopes[len(scopes) - 1]
      else:
        scope = self.scope
      xml += OneLine(Dict.scope, scope)
    if self.optional:
      xml += OneLine(Dict.optional, Dict.true)

    if self.exclusions:
      xml += '  ' + Dict.exclusionsStartTag + Dict.newLine
      for e in self.exclusions:
        xml += '    ' + Dict.exclusionStartTag + Dict.newLine
        xml += OneLine(Dict.groupId, e.groupId, 6)
        xml += OneLine(Dict.artifactId, e.artifactId, 6)
        xml += '    ' + Dict.exclusionEndTag + Dict.newLine
      xml += '  ' + Dict.exclusionsEndTag + Dict.newLine

    xml += Dict.dependencyEndTag + Dict.newLine
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
    except Exception:
      pass
    return PackageId(groupId, artifactId, version, type)

  @staticmethod
  def __Override(package, **tparams):
    if Dict.artifactId in tparams: package.artifactId = tparams.get(Dict.artifactId)
    if Dict.groupId in tparams: package.groupId = tparams.get(Dict.groupId)
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
      newPackage.__setattr__(name, packageData[name])
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
    return self.AsStr()

  def __hash__(self):
    return hash(repr(self))

  def __repr__(self):
    return '%s:%s.%s:%s (%s, %s, %s, (%s))' % (str(self.groupId), str(self.artifactId), str(self.type), str(self.version),
                                              str(self.stamp), str(self.scope), str(self.optional),
                                              ','.join([repr(p) for p in self.exclusions]))

