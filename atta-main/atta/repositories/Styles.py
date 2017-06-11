""".. no-user-reference:"""
from .. import Dict

class IRepositoryStyle:
  """TODO: description"""
  def DirName(self, package):
    assert False
  def FileName(self, package):
    assert False
  def FullFileName(self, package):
    assert False

class Maven(IRepositoryStyle):
  """TODO: description"""
  def DirName(self, package):
    return '%s/%s/%s' % (str(package.groupId).replace('.', '/'), str(package.artifactId), str(package.version))

  def FileName(self, package):
    fn = str(package.artifactId)
    if bool(package.version):
      fn += '-' + str(package.version)
    if bool(package.tests):
      fn += '-tests'
    if bool(package.type):
      type = str(package.type)
      if bool(package.tests):
        type = type.replace('test-', '').replace('tests-', '')
      if type == Dict.bundle:
        type = Dict.jar
      fn += '.' + type
    return fn

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
class ByArtifactId(Flat):
  """TODO: description"""
  def DirName(self, package):
    return '%s' % (str(package.artifactId))

# TODO: lepsza nazwa?
class ByVersion(Flat):
  """TODO: description"""
  def DirName(self, package):
    return '%s' % (str(package.version))

class OnlyFileName(Flat):
  """TODO: description"""
  def DirName(self, package):
    return ''

class PyPI(Flat):
  """TODO: description"""
  def DirName(self, package):
    return 'packages/source/%s/%s' % (str(package.artifactId)[0], str(package.artifactId))

class GitHub(Flat):
  """TODO: description"""
  def DirName(self, package):
    #https://github.com/boguslawski-piotr/atta/tarball/v0.2.2
    #https://github.com/boguslawski-piotr/atta/zipball/v0.2.2
    #https://github.com/boguslawski-piotr/atta/tarball/master
    #https://github.com/boguslawski-piotr/atta/zipball/master
    dirName = '%s/%s' % (str(package.groupId), str(package.artifactId))
    if package.type == Dict.targzExt:
      dirName += '/tarball/'
    elif package.type == Dict.zipExt:
      dirName += '/zipball/'
    if package.version != 'master':
      dirName += 'v'
    dirName += str(package.version)
    return dirName
