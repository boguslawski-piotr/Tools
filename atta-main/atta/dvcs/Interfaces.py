'''.. no-user-reference:'''

class IDvcs:
  '''TODO: description'''

  '''High level api useful in build scripts'''
  
  def IsWorkingDirectoryClean(self):
    '''TODO: description'''
    pass
  
  def UpdateWorkingDirectory(self, revision = None, remote = None, **tparams):
    '''TODO: description'''
    pass
  
  def SetTag(self, tagName, msg = None, replace = False, **tparams):
    '''TODO: description'''
    pass
  
  def CommitAndPublishAllChanges(self, msg, author = None, remotes = None, **tparams):
    '''TODO: description'''
    pass
  
  '''Normal level api'''
  
  '''Low level api'''

  def Cmd(self, params, **tparams):
    '''TODO: description'''
    pass
  
  