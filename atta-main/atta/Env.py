import sys
import os

from tools.Misc import LogLevel, Logger
from atta import *

class Env(dict):
  '''
  Env class 
     
  TODO: description
  '''
  def __init__(self, environ):
    dict.__init__(self, environ)
    self['cwd'] = os.getcwd()
    
  def chdir(self, path):
    '''TODO: description'''
    prevDir = os.getcwd()
    os.chdir(path)
    self['cwd'] = os.getcwd()
    return prevDir
  
  '''private section'''
  
  def _Dump(self):
    Atta.logger.Log('*** Env', level = LogLevel.DEBUG)
    for key, value in self.iteritems():
      Atta.logger.Log('Env.' + key + ' = ' + value, level = LogLevel.DEBUG)
    Atta.logger.Log('***', level = LogLevel.DEBUG)
