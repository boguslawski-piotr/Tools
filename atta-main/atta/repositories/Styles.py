'''.. no-user-reference:'''

from .Interfaces import IRepositoryStyle

class Maven(IRepositoryStyle):
  def DirName(self, packageId):
    return '%s/%s/%s' % (str(packageId.groupId).replace('.', '/'), str(packageId.artifactId), str(packageId.version))

  def FileName(self, packageId):
    return '%s-%s.%s' % (str(packageId.artifactId), str(packageId.version), str(packageId.type))

  def FullFileName(self, packageId):
    return '%s/%s' % (self.DirName(packageId), self.FileName(packageId))

class Flat(Maven):
  def DirName(self, packageId):
    if packageId.groupId is None or packageId.groupId == packageId.artifactId:
      return '%s-%s' % (str(packageId.artifactId), str(packageId.version))
    else:
      return '%s.%s-%s' % (str(packageId.groupId), str(packageId.artifactId), str(packageId.version))
