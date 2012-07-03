'''.. Miscellaneous: Supports versions'''
import os
import sys
import OS
from VariablesLikeAntExpander import Expander
from Properties import Properties

class Version:
  def __init__(self, conf = {}):
    self.Configure(conf)
  
  def __str__(self):
    '''TODO: description'''
    e = Expander()
    return e.Expand(self.format, 
                    major = self.major, 
                    minor = self.minor, 
                    patch = self.patch, 
                    build = self.build,
                    prefix = self.prefix if self.usePrefix else '',
                    postfix = self.postfix if self.usePostfix else '')
  
  def Configure(self, conf):
    self.major = 0
    self.minor = 0
    self.patch = 0
    self.build = 0
    self.changed = False
    
    self.masterFileName = conf.get('master', 'version.info')
    if not self.ReadMaster():
      self.UpdateMaster()
    
    self.format = conf.get('format', '${major}.${minor}.${build}')
    
    self.prefix = conf.get('prefix', '')
    self.usePrefix = True
    self.postfix = conf.get('postfix', '')
    self.usePostfix = True
    
  def NextMajor(self):
    '''Increase major number, update all registered files (if needed) and master file.'''
    self.major += 1
    self.ForceUpdateAll()

  def NextMinor(self):
    '''Increase minor number, update all registered files (if needed) and master file.'''
    self.minor += 1
    self.ForceUpdateAll()

  def NextPatch(self):
    '''Increase patch number, update all registered files (if needed) and master file.'''
    self.patch += 1
    self.ForceUpdateAll()

  def NextBuild(self):
    '''Increase build number, update all registered files (if needed) and master file.'''
    self.build += 1
    self.ForceUpdateAll()
  
  def SetPrefix(self, prefix):
    self.prefix = prefix
    
  def UsePrefix(self, use):
    self.usePrefix = use
  
  def SetPostfix(self, postfix):
    self.postfix = postfix
    
  def UsePostfix(self, use):
    self.usePostfix = use
  
  def ReadMaster(self):
    if not os.path.exists(self.masterFileName):
      return False
    with Properties().Open(self.masterFileName) as p:
      self.major = int(p.Get('major', 0))
      self.minor = int(p.Get('minor', 0))
      self.patch = int(p.Get('patch', 0))
      self.build = int(p.Get('build', 0))
      return True
    
  def UpdateMaster(self):
    if not self.changed:
      return True
    with Properties().Create(self.masterFileName) as p:
      p.Set('major', self.major)
      p.Set('minor', self.minor)
      p.Set('patch', self.patch)
      p.Set('build', self.build)
      p.Save()
      self.changed = False
      return True
    
  def ForceUpdateMaster(self):
    self.changed = True
    self.UpdateMaster()

  def UpdateAll(self):
    self.UpdateMaster()

  def ForceUpdateAll(self):
    self.changed = True
    self.UpdateAll()
    