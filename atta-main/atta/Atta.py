import sys
import os
from datetime import datetime
import atta
import atta.StdLogger
from atta.Log import *
from atta.Project import Project

## Atta class 
#  TODO: description
class Atta():
  def __init__(self, environ, dirName, argv):
    if LoggerBridge.LoggerClass is None:
      LoggerBridge.LoggerClass = atta.StdLogger.Logger
    
    self.name = 'Atta'
    self.description = ''
    
    #!v:
    self.versionName = '0.2'
    #!
    
    va = self.versionName.split('.')
    self.version = int(self.versionName.replace('.', ''))  
    
    self.environ = environ
    self.dirName = dirName
    self.argv = argv
    
    self.args = self._ParseArgv(self.argv)
    
    if self.args.ll:
      LogLevel.actual = self.args.ll[0]

    if self.args.lc:
      script = 'import ' + self.args.lc[0] + \
               '\nLoggerBridge.LoggerClass = ' + self.args.lc[0] + '.Logger\n'
      exec(script)
    
    self._Dump()
  
  def Run(self):
    prevAttaAtta = atta.atta
    try:
      atta.atta = self
      project = Project()
      project._Run(self.environ, self.args.f[0], self.args.target)
    except:
      raise
    finally:
      atta.atta = prevAttaAtta
  
  ## \privatesection

  def _ParseArgv(self, argv):
    import argparse
    
    argsParser = argparse.ArgumentParser(
      prog = self.name,
      formatter_class = argparse.RawDescriptionHelpFormatter,
      description = self.name + ' v' + self.versionName + os.linesep + self.description, 
      epilog = 'Bugs, comments and suggestions, please report on page\nhttps://github.com/boguslawski-piotr/Atta/issues'
    )
    
    argsParser.add_argument(
      'target', nargs = '*', default = '',
      help = ''
    )
    argsParser.add_argument(
      '-f', nargs = 1, default = ['build.py'], metavar = 'file',
      help = 'use given buildfile'
    )
    argsParser.add_argument(
      '-ll', nargs = 1, metavar = 'level', type = int, choices = [0,1,2,3,4], 
      help = 'log level'
    )
    argsParser.add_argument(
      '-lc', nargs = 1, metavar = 'module',
      help = 'use given Logger class from module'
    )
    
    args, argv = argsParser.parse_known_args(argv)
    if argv:
        _msg = _('unrecognized arguments: %s')
        argsParser.error(_msg % ' '.join(argv))
    return args
    
  def _Dump(self):
    Log('Atta.versionName = ' + self.versionName, level = LogLevel.DEBUG)
    Log('Atta.version = ' + str(self.version), level = LogLevel.DEBUG)
    Log("Atta.args = {0}".format(self.args), level = LogLevel.DEBUG)

