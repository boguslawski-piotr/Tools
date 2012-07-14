'''TODO: description'''
import sys
import os

from . import Atta, LogLevel

class Env(dict):
  '''
  Env class 
     
  TODO: description
  '''
  def __init__(self, environ):
    dict.__init__(self, environ)
    self['cwd'] = os.getcwd()

  def chdir(self, dirName):
    '''TODO: description'''
    prevDirName = os.getcwd()
    os.chdir(dirName)
    self['cwd'] = os.getcwd()
    return prevDirName

  '''private section'''

  def _Dump(self):
    Atta.Log('*** Env', level = LogLevel.DEBUG)
    for key, value in self.iteritems():
      Atta.Log('Env.' + key + ' = ' + value, level = LogLevel.DEBUG)
    Atta.Log('***', level = LogLevel.DEBUG)
