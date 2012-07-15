""".. no-user-reference:"""

class IDvcs:
  """TODO: description"""

  '''High level api useful in build scripts'''

  def IsWorkingDirectoryClean(self):
    """TODO: description"""
    pass

  def UpdateWorkingDirectory(self, revision = None, remote = None, **tparams):
    """TODO: description
    Sets self.someChangesWereTaken to 0 if WD is up-to-date, 1 if some changes were pulled, -1 we do not known
    """
    pass

  def SetTag(self, tagName, msg = None, replace = False, **tparams):
    """TODO: description"""
    pass

  def CommitAndPublishAllChanges(self, msg, author = None, remotes = None, **tparams):
    """TODO: description"""
    pass

  '''Normal level api'''

  '''Low level api'''

  def Cmd(self, params, **tparams):
    """TODO: description"""
    pass

