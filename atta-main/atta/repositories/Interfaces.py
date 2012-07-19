""".. no-user-reference:"""

class IRepositoryStyle:
  """TODO: description"""
  def DirName(self, package):
    assert False
  def FileName(self, package):
    assert False
  def FullFileName(self, package):
    assert False

# TODO: give more accurate name
class IPackageUrls:
  """TODO: description"""
  def StampUrl(self, package):
    assert False
  def PackageUrl(self, package):
    assert False
