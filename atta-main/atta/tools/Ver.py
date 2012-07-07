'''.. Miscellaneous: Project version management'''
import os

from ..tasks.Base import Task
from .. import Dict
from .. import LogLevel
from .internal.Misc import ObjectFromClass
from .DefaultVarsExpander import Expander
from .Properties import Properties
from .Misc import isiterable
from .Strategies import VersionDefaultStrategy

class Version(Task):
  '''TODO: description'''
  def __init__(self, **conf):
    self.Configure(**conf)
  
  def Configure(self, **conf):
    '''TODO: description'''
    self._impl = ObjectFromClass(conf.get('impl', Version.GetDefaultImpl()))
    
    listeners = conf.get('listeners', [])
    if not isiterable(listeners):
      listeners = [listeners]
    self._listeners = []
    for _class in listeners:
      self.RegisterListener(_class)
      
    self.major = 0
    self.minor = 0
    self.patch = 0
    self.build = 0
    self.changed = False
    
    self.fileName = conf.get('fileName', 'version.info')
    if not self._Read():
      if conf.get('createIfNotExists', True):
        self._ForceUpdate()
    
    self.format = conf.get('format', '${major}.${minor}.${patch}.${build}')
    
    self.prefix = conf.get('prefix', '')
    self.postfix = conf.get('postfix', '')
    
    self._RunListeners('AfterConfigure')
    
  def __del__(self):
    self._Update()
    
  def AsStr(self):
    '''TODO: description'''
    return str(self)
  
  def __str__(self):
    '''TODO: description'''
    e = Expander()
    return e.Expand(self.format, 
                    major = self.major, 
                    minor = self.minor, 
                    patch = self.patch, 
                    build = self.build,
                    prefix = self.prefix,
                    postfix = self.postfix)
  
  def NextMajor(self, update = True):
    '''TODO: description'''
    old = self._AsStr()
    self._impl.GetObject().NextMajor(self)
    self._RunListeners('NextMajor')
    self._Changed(update, old)
    
  def NextMinor(self, update = True):
    '''TODO: description'''
    old = self._AsStr()
    self._impl.GetObject().NextMinor(self)
    self._RunListeners('NextMinor')
    self._Changed(update, old)

  def NextPatch(self, update = True):
    '''TODO: description'''
    old = self._AsStr()
    self._impl.GetObject().NextPatch(self)
    self._RunListeners('NextPatch')
    self._Changed(update, old)
    
  def NextBuild(self, update = True):
    '''TODO: description'''
    old = self._AsStr()
    self._impl.GetObject().NextBuild(self)
    self._RunListeners('NextBuild')
    self._Changed(update, old)

  def SetPrefix(self, prefix):
    '''TODO: description'''
    old = self.prefix
    self.prefix = prefix
    self._RunListeners('SetPrefix')
    return old
  
  def SetPostfix(self, postfix):
    '''TODO: description'''
    old = self.postfix
    self.postfix = postfix
    self._RunListeners('SetPostfix')
    return old
  
  def RegisterListener(self, _class):
    '''TODO: description'''
    listener = ObjectFromClass(_class)
    self._listeners.append(listener)
    return listener
  
  def UnRegisterListener(self, listener):
    '''TODO: description'''
    i = self._listeners.index(listener)
    del self._listeners[i]

  def ExpandVariables(self, data):
    '''TODO: description'''
    e = Expander()
    return e.Expand(data, 
                    major   = self.major, 
                    minor   = self.minor, 
                    patch   = self.patch, 
                    build   = self.build,
                    prefix  = self.prefix,
                    postfix = self.postfix,
                    version = str(self))
  
  class FileFilter:
    '''TODO: description'''
    def __init__(self, srcFileName, destFileName):
      self.srcFileName = srcFileName
      self.destFileName = destFileName
    
    def __call__(self, v):
      self.Run(v)
      
    def Run(self, v):
      with open(self.srcFileName, 'rb') as f:
        data = f.read()
      data = v.ExpandVariables(data)
      with open(self.destFileName, 'wb') as f:
        f.write(data)
      
  _defaultImpl = ObjectFromClass(VersionDefaultStrategy) 

  @staticmethod
  def SetDefaultImpl(_class):
    '''TODO: description'''
    Version._defaultImpl = ObjectFromClass(_class)

  @staticmethod
  def GetDefaultImpl():
    '''TODO: description'''
    return Version._defaultImpl.GetClass()

  '''private section'''

  def _Changed(self, forceUpdate, old = None):
    if forceUpdate: 
      self._ForceUpdate()
      if old:
        self.Log(Dict.msgChangedFromXToYInZ % (old, self._AsStr(), self.fileName), level = LogLevel.INFO)
    else: 
      self.changed = True
  
  # TODO: odczyt i zapis w taki sposob aby w tym pliku mozna bylo umieszczac inne rzeczy
  # np. z oznaczeniem bloku: #!version: ... #:version!
  
  def _Read(self):
    if not os.path.exists(self.fileName):
      return False
    p = Properties().Open(self.fileName)
    self.major = int(p.Get('major', 0))
    self.minor = int(p.Get('minor', 0))
    self.patch = int(p.Get('patch', 0))
    self.build = int(p.Get('build', 0))
    self._RunListeners('AfterRead')
    return True
    
  def _Update(self):
    if not self.changed:
      return True
    self._RunListeners('BeforeUpdate')
    p = Properties().Create(self.fileName)
    p.Set('major', self.major)
    p.Set('minor', self.minor)
    p.Set('patch', self.patch)
    p.Set('build', self.build)
    p.Save()
    self.changed = False
    self._RunListeners('AfterUpdate')
    return True
    
  def _ForceUpdate(self):
    self.changed = True
    self._Update()

  def _RunListeners(self, action):
    for l in self._listeners:
      if action in dir(l.GetObject()):
        exec('l.GetObject().' + action + '(self)')
        
  def _CreateIfNotExists(self):
    if not os.path.exists(self.fileName):
      self._ForceUpdate()
      
  def _AsStr(self):
    return '%d.%d.%d.%d' % (self.major, self.minor, self.patch, self.build)
  
  def _FromStr(self, v):
    self.major, self.minor, self.patch, self.build = v.split('.')
