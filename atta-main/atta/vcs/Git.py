""".. Distributed Version Control Systems: Git"""
import os

from .. import LogLevel, Dict, OS, Task, Exec
from . import Interfaces

class Git(Interfaces.IVcs, Task):
  """TODO: description"""
  def __init__(self, dirName = '.', params = None, **tparams):
    self._lastRevision = None
    self._lastRemote = None
    self._tagWasSet = False

    self.output = None
    self.someChangesWereTaken = -1

    self.dirName = dirName if dirName else '.'
    if params:
      self.Cmd(params, **tparams)

  def IsWorkingDirectoryClean(self):
    self.Cmd(['status', '--porcelain'], logOutput = False)
    return len(self.output.strip()) <= 0

  def UpdateWorkingDirectory(self, revision = None, remote = None, **tparams):
    self._SetLogOutput(tparams)

    checkoutOutput = ''
    if revision:
      if self.Cmd(['checkout', revision], **tparams) != 0:
        return self.returnCode
      checkoutOutput = self.output
      self._lastRevision = revision

    if self.Cmd(['pull', remote if remote else ''], **tparams) == 0:
      self._lastRemote = remote
      self.someChangesWereTaken = int(self.output.find('up-to-date') < 0)

    self.output = checkoutOutput + Dict.newLine + self.output
    return self.returnCode

  def SetTag(self, tagName, msg = None, replace = False, **tparams):
    self._SetLogOutput(tparams)
    params = ['tag', '-f' if replace else '']
    if msg:
      params += ['-a', '-m', msg]
    params += [tagName]
    if self.Cmd(params, **tparams) == 0:
      self._tagWasSet = True
    return self.returnCode

  def CommitAndPublishAllChanges(self, msg, author = None, remotes = None, **tparams):
    self._SetLogOutput(tparams)

    if self.Cmd('add .', **tparams) != 0:
      return self.returnCode
    addOutput = self.output

    params = ['commit', '-a', '-m', msg]
    if author:
      params += ['--author=' + author]
    self.Cmd(params, **tparams)
    commitOutput = self.output
    if self.returnCode != 0:
      self.output = addOutput + Dict.newLine + commitOutput
      return self.returnCode

    if not remotes:
      remotes = [self._lastRemote if self._lastRemote else 'origin']
    else:
      remotes = OS.Path.AsList(remotes, ' ')
    revision = self._lastRevision
    if not revision:
      revision = 'HEAD'
    pushOutput = ''
    for remote in remotes:
      params = ['push', '--tags' if self._tagWasSet else '', remote, revision]
      self.Cmd(params, **tparams)
      pushOutput = pushOutput + Dict.newLine + self.output
      if self.returnCode != 0:
        self.output = addOutput + Dict.newLine + commitOutput + Dict.newLine + pushOutput
        return self.returnCode

    self._tagWasSet = False
    self.someChangesWereTaken = int(False)
    self.output = addOutput + Dict.newLine + commitOutput + Dict.newLine + pushOutput
    return self.returnCode

  def Cmd(self, params, **tparams):
    """TODO: description"""
    params = OS.Path.AsList(params, ' ')
    params = [p for p in params if len(p) > 0]

    if self.LogLevel() <= LogLevel.INFO:
      self.Log(Dict.msgDvcsRepository % os.path.realpath(self.dirName), level = LogLevel.VERBOSE)
      self.Log(' '.join(params))

    e = Exec(self.GetExecutable(**tparams), params, dirName = self.dirName, **tparams)
    self.returnCode = e.returnCode
    self.output = self._NormalizeOutput(e.output)

    if self.LogLevel() <= LogLevel.VERBOSE:
      if not tparams.get(Dict.paramLogOutput):
        if len(self.output): self.Log(self.output)
        self.Log(Dict.msgExitCode.format(self.returnCode))

    return self.returnCode

  def GetExecutable(self, **tparams):
    executable = self.Env().which(Dict.GIT_EXE_IN_PATH)
    return executable if executable else Dict.GIT_EXE

  '''private section'''

  def _SetLogOutput(self, tparams):
    if not Dict.paramLogOutput in tparams:
      tparams[Dict.paramLogOutput] = False

  def _NormalizeOutput(self, output):
    return output.replace(chr(0x1B) + '[K', '\n')
