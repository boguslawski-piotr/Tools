""".. no-user-reference:"""

class IVcs:
  """TODO: description"""

  # High level api useful in build scripts

  def IsWorkingDirectoryClean(self):
    """TODO: description"""
    assert False

  def UpdateWorkingDirectory(self, revision = None, remote = None, **tparams):
    """TODO: description
    Must sets self.someChangesWereTaken to 0 if WD is up-to-date, 1 if some changes were pulled, -1 we do not known
    """
    assert False

  def SetTag(self, tagName, msg = None, replace = False, **tparams):
    """TODO: description"""
    assert False

  def CommitAndPublishAllChanges(self, msg, author = None, remotes = None, **tparams):
    """TODO: description"""
    assert False

  # Normal level api

  # Low level api

  def Cmd(self, params, **tparams):
    """TODO: description"""
    assert False

