import platform
import sys
import os

import atta
import OS
from Log import LogLevel, Log, LoggerBridge
from Properties import Properties
from Project import Project

## Atta class 
#  TODO: description
class Atta():
  def __init__(self, environ, dirName, argv):
    self.name = 'Atta'
    self.description = ''
    
    self.versionName = '0.2'
    self.version = int(self.versionName.replace('.', ''))  
    
    self.environ = environ
    self.dirName = dirName
    
    prop = Properties().Open(os.path.join(self.dirName, 'atta.properties'))
    
    args = prop.Get('args', None)
    if args is not None:
      argv += args.split(' ')
    print argv
    self.args = self._ParseArgv(argv)
    
    if self.args.ll:
      LogLevel.actual = self.args.ll[0]

    if self.args.lc:
      __import__(OS.RemoveExt(self.args.lc[0]))
      LoggerBridge.SetLoggerClass(self.args.lc[0])
    
    self._Dump()
  
  def Run(self):
    prevAttaAtta = atta.attai
    try:
      atta.attai = self
      _project = Project()
      _project._Run(self.environ, self.args.f[0], self.args.target)
      return 0
    
    except Exception, e:
      if self.args.scs or LogLevel.actual <= LogLevel.VERBOSE:
        raise
      else:
        Log(e, level = LogLevel.ERROR)
        return 1
    
    finally:
      atta.attai = prevAttaAtta
  
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
      '-lc', nargs = 1, metavar = 'class',
      help = 'use given class as logger (must implements ILogger interface)'
    )
    argsParser.add_argument(
      '-scs', action = 'store_true',
      help = 'shows call stack (traceback) on error')
    argsParser.add_argument(
      '-ll', nargs = 1, metavar = 'level', type = int, choices = [0,1,2,3,4], 
      help = 'sets the log level'
    )
    
    args, argv = argsParser.parse_known_args(argv)
    if argv:
      _msg = _('unrecognized arguments: %s')
      argsParser.error(_msg % ' '.join(argv))
    
    return args
    
  def _Dump(self):
    Log('*** Atta', level = LogLevel.DEBUG)
    Log('Platform.platform = ' + platform.platform(), level = LogLevel.DEBUG)
    Log('Platform.system = ' + platform.system(), level = LogLevel.DEBUG)
    Log('Python.versionName = ' + platform.python_version(), level = LogLevel.DEBUG)
    Log('Atta.versionName = ' + self.versionName, level = LogLevel.DEBUG)
    Log('Atta.version = ' + str(self.version), level = LogLevel.DEBUG)
    Log('Atta.dirName = ' + self.dirName, level = LogLevel.DEBUG)
    Log("Atta.args = {0}".format(self.args), level = LogLevel.DEBUG)
    Log('***', level = LogLevel.DEBUG)

