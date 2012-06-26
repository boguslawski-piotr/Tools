'''
Various interfaces and base classes.
'''
import tools.OS as OS

class ILogger:
  '''
  Logger interface  
  
  special arguments
  
  project
    start
    end
    msg
    
    status
    at
    time
    exception
    
  target
    prepare
    start
    end
    finalize
    msg
    
  task
  ''' 
  def Log(self, msg, **args):
    pass
  
#------------------------------------------------------------------------------ 

class IVariablesExpander:
  '''
  IVariablesExpander interface
  
  TODO: description
  '''
  def Expand(self, txt, **tparams): 
    pass  
  
#------------------------------------------------------------------------------ 

class IRepository:
  '''TODO: description'''
  def Get(self, groupId, artifactId, version, type, store = None, **tparams):
    pass
  
  def Check(self, groupId, artifactId, version, type, timestamp, **tparams):
    pass
  
  def Put(self, f, timestamp, groupId, artifactId, version, type, **tparams):
    pass
  
  def Clean(self, groupId, artifactId, version, type): 
    pass
    
  def _Name(self):
    pass
  
  ''' 
  A few useful tools.
  IMO does not make sense to create a separate class, 
  because these methods are static and do not 
  interfere with the concept of the interface.
  '''
  
  @staticmethod
  def DisplayName(groupId, artifactId, version, type):
    return '%s:%s.%s:%s' % (groupId, artifactId, type, version)

  @staticmethod
  def ResolveDisplayName(package):
    groupId = ''
    artifactId = ''
    type = ''
    version = ''
    try:
      items = package.split(':')
      if len(items) == 3:
        groupId = items[0]
        del items[0]
      type= OS.Path.Ext(items[0])
      artifactId = OS.Path.RemoveExt(items[0])
      if groupId == '':
        groupId = artifactId
      version = items[1]
    except:
      pass
    return (groupId, artifactId, type, version)
  
#------------------------------------------------------------------------------ 

import atta

class Activity:
  '''
  Base class for all targets, tasks and other executive classes.
     
  TODO: description
  '''
  def Log(self, msg = '', **args):
    self._Log(msg, **args)

  def LogIterable(self, msg = '', iterable = [], **args):
    self._LogIterable(msg, iterable, **args)
  
  '''private section'''
    
  def _Type(self):
    return ''

  def _Name(self):
    return ''
  
  def _Log(self, msg = '', **args):
    args[self._Type()] = self._Name()
    atta.Atta.logger.Log(msg, **args)

  def _LogIterable(self, msg = '', iterable = [], **args):
    args[self._Type()] = self._Name()
    atta.Atta.logger.LogIterable(msg, iterable, **args)
