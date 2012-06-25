import os, cStringIO, ConfigParser
import sys

class Properties:
  '''
  Supports the Java properties files.
  '''
  
  def Open(self, fileName):
    '''Reads a property list (key and element pairs) from the file.'''
    f = cStringIO.StringIO()
    f.write('[p]\n')
    f.write(open(fileName, 'r').read())
    f.seek(0, os.SEEK_SET)
    self.c = ConfigParser.RawConfigParser()
    self.c.readfp(f)
    f.close()
    return self

  def Get(self, name, default = None):
    '''
    Searches for the property with the specified `name`. 
    The method returns the `default` value argument if the property is not found.
    ''' 
    try:
      return self.c.get('p', name)
    except:
      return default
    
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

       