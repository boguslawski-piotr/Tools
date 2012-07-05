'''.. Version Control: Git'''
from ..tasks.Base import Task
from ..tasks.Exec import Exec
import atta.Dict as Dict
from atta import GetProject
import atta.tools.OS as OS
import Interfaces

class Git(Interfaces.IDvcs, Task):
  def __init__(self, dir = '.', params = None, **tparams):
    self._lastRevision = None
    self._lastRemote = None 
    self._tagWasSet = False

    self.dir = dir if len(dir) > 0 else '.'
    if params != None:
      self.Cmd(params, **tparams)
      
  def IsWorkingDirectoryClean(self):
    self.Cmd(['status', '--porcelain'], logOutput = False)
    return len(self.output.strip()) <= 0

  def UpdateWorkingDirectory(self, revision = None, remote = None, **tparams):
    self._SetLogOutput(tparams)
    
    checkoutOutput = ''
    if revision != None:
      if self.Cmd(['checkout', revision], **tparams) != 0:
        return self.returnCode
      checkoutOutput = self.output
      self._lastRevision = revision
      
    self.Cmd(['pull', remote if remote != None else ''], **tparams)
    self._lastRemote = remote
    
    self.output = checkoutOutput + Dict.newLine + self.output
    return self.returnCode
  
  def SetTag(self, tagName, msg = None, replace = False, **tparams):
    self._SetLogOutput(tparams)
    params = ['tag', '-f' if replace else '']
    if msg != None and len(msg) > 0: 
      params += ['-a', '-m', msg]
    params += [tagName]
    self.Cmd(params, **tparams)
    if self.returnCode == 0: 
      self._tagWasSet = True
    return self.returnCode
  
  def CommitAndPublishAllChanges(self, msg, author = None, remotes = None, **tparams):
    self._SetLogOutput(tparams)
    
    if self.Cmd('add .', **tparams) != 0:
      return self.returnCode
    addOutput = self.output
    
    params = ['commit', '-a', '-m', msg]
    if author != None:
      params += ['--author=' + author]
    if self.Cmd(params, **tparams) != 0:
      return self.returnCode
    commitOutput = self.output
    self.output = addOutput + Dict.newLine + commitOutput
    
    if remotes == None:
      remotes = [self._lastRemote if self._lastRemote != None else 'origin']
    revision = self._lastRevision
    if revision == None:
      revision = 'HEAD'
    pushOutput = ''
    for remote in remotes:
      params = ['push', '--tags' if self._tagWasSet else '', remote, revision]
      if self.Cmd(params, **tparams) != 0:
        return self.returnCode
      pushOutput = pushOutput + self.output
      
    self._tagWasSet = False
    self.output = addOutput + Dict.newLine + commitOutput + Dict.newLine + pushOutput
    return self.returnCode
  
  def Cmd(self, params, **tparams):
    '''TODO: description'''
    params = OS.Path.AsList(params, ' ')
    self._DumpParams(locals())
    
    ocwd = GetProject().env.chdir(self.dir)
    try:
      e = Exec(self.GetExecutable(**tparams), [p for p in params if len(p) > 0], **tparams)
    finally:
      GetProject().env.chdir(ocwd)
      
    self.returnCode = e.returnCode
    self.output = e.output
    return self.returnCode
  
  def GetExecutable(self, **tparams):
    return 'git'
    
  def _SetLogOutput(self, tparams):
    if not Dict.paramLogOutput in tparams:
      tparams[Dict.paramLogOutput] = False
      
    