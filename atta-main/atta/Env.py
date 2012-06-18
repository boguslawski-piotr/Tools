import sys
import os

from atta.OS import *
from atta.Log import *
import atta

## Env class 
#  TODO: description
class Env():
  def __init__(self, environ):
    self.vars = environ

  def chdir(self, path):
    prevDir = os.getcwd()
    os.chdir(path)
    self['cwd'] = os.getcwd()
    return prevDir
  
  def iteritems(self):
    return self.vars.iteritems()
  
  def iterkeys(self):
    return self.vars.iterkeys()
  
  def itervalues(self):
    return self.vars.itervalues()
  
  ## \privatesection
  
  def __setitem__(self, key, item):
    return self.vars.__setitem__(key, item)
  
  def __getitem__(self, key):
    return self.vars.__getitem__(key)
  
  def _Dump(self):
    for key, value in self.vars.iteritems():
      Log('Env.' + key + ' = ' + value, level = LogLevel.DEBUG)
