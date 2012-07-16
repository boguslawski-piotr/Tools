""".. no-user-reference:"""

from .Interfaces import IRepositoryStyle

class Maven(IRepositoryStyle):
  """TODO: description"""
  def DirName(self, package):
    return '%s/%s/%s' % (str(package.groupId).replace('.', '/'), str(package.artifactId), str(package.version))

  def FileName(self, package):
    fn = str(package.artifactId) + '-' + str(package.version)
    if bool(package.type):
      fn = fn + '.' + str(package.type)
    return fn
    #return '%s-%s.%s' % (str(package.artifactId), str(package.version), str(package.type))

  def FullFileName(self, package):
    dirName = self.DirName(package).strip()
    if dirName:
      return dirName + '/' + self.FileName(package)
    else:
      return self.FileName(package)

class Flat(Maven):
  """TODO: description"""
  def DirName(self, package):
    if not package.groupId or package.groupId == package.artifactId:
      return '%s-%s' % (str(package.artifactId), str(package.version))
    else:
      return '%s.%s-%s' % (str(package.groupId), str(package.artifactId), str(package.version))

# TODO: lepsza nazwa?
class ByVersion(Flat):
  """TODO: description"""
  def DirName(self, package):
    return '%s' % (str(package.version))

class OnlyFileName(Flat):
  """TODO: description"""
  def DirName(self, package):
    return ''
