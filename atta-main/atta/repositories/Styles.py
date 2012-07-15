""".. no-user-reference:"""

from .Interfaces import IRepositoryStyle

class Maven(IRepositoryStyle):
  """TODO: description"""
  def DirName(self, packageId):
    return '%s/%s/%s' % (str(packageId.groupId).replace('.', '/'), str(packageId.artifactId), str(packageId.version))

  def FileName(self, packageId):
    fn = str(packageId.artifactId) + '-' + str(packageId.version)
    if bool(packageId.type):
      fn = fn + '.' + str(packageId.type)
    return fn
    #return '%s-%s.%s' % (str(packageId.artifactId), str(packageId.version), str(packageId.type))

  def FullFileName(self, packageId):
    dirName = self.DirName(packageId).strip()
    if dirName:
      return dirName + '/' + self.FileName(packageId)
    else:
      return self.FileName(packageId)

class Flat(Maven):
  """TODO: description"""
  def DirName(self, packageId):
    if not packageId.groupId or packageId.groupId == packageId.artifactId:
      return '%s-%s' % (str(packageId.artifactId), str(packageId.version))
    else:
      return '%s.%s-%s' % (str(packageId.groupId), str(packageId.artifactId), str(packageId.version))

# TODO: lepsza nazwa?
class ByVersion(Flat):
  def DirName(self, packageId):
    return '%s' % (str(packageId.version))

class OnlyFileName(Flat):
  """TODO: description"""
  def DirName(self, packageId):
    return ''
