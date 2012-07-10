'''.. Miscellaneous: Supports the Java properties files'''
import os, cStringIO, ConfigParser
import sys

from . import OS

class Properties:
  '''
  Supports the Java properties files.
  '''
  def __init__(self):
    self.c = None
    self.fileName = None
    
  @staticmethod
  def Create(fileName):
    '''Creates empty Properties object. TODO: ''' 
    p = Properties()
    p.c = ConfigParser.RawConfigParser()
    p.c.add_section('p')
    p.fileName = fileName
    return p
  
  @staticmethod
  def Open(fileName):
    '''Creates Properties object and reads a property list (key and element pairs) from the file.'''
    f = cStringIO.StringIO()
    f.write('[p]\n')
    f.write(open(fileName, 'r').read())
    f.seek(0, os.SEEK_SET)
    p = Properties()
    p.c = ConfigParser.RawConfigParser()
    p.c.readfp(f)
    f.close()
    p.fileName = fileName
    return p

  def Get(self, name, default = None):
    '''
    Searches for the property with the specified `name`. 
    The method returns the `default` value argument if the property is not found.
    ''' 
    try:
      return self.c.get('p', name)
    except:
      return default

  def Set(self, name, value):
    '''TODO: description'''
    self.c.set('p', name, value)
  
  def Save(self, force = True):
    '''TODO: description'''
    if force:
      OS.SetReadOnly(self.fileName, False)
    with open(self.fileName, 'wb') as f:
      for (key, value) in self.c.items('p'):
        if key == "__name__":
          continue
        key = " = ".join((key, str(value).replace('\n', '\n\t')))
        f.write("%s\n" % (key))
      f.write("\n")
    
  def __enter__(self):
    return self
  
  def __exit__(self, exc_type, exc_value, traceback):
    return False
    
#------------------------------------------------------------------------------ 

def mgetattr(moduleName, attrName, default):
  '''TODO: description'''
  module = sys.modules[moduleName]
  if hasattr(module, attrName):
    return getattr(module, attrName, default)
  return default
    
def msetattr(moduleName, attrName, value):
  '''TODO: description'''
  module = sys.modules[moduleName]
  setattr(module, attrName, value)
