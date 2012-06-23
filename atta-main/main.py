#!/usr/bin/python
'''
Atta main
'''

import platform
import sys
import os

from atta.tools.Properties import Properties
from atta.tools.Misc import LogLevel
import atta.tools.OS as OS
from atta import *
from atta.Project import Project

def _ParseArgv(argv):
  import argparse
  
  argsParser = argparse.ArgumentParser(
    prog = Atta.name,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = Atta.name 
                  + ' v' + Atta.versionName 
                  + os.linesep 
                  + Atta.description, 
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
    print(Atta.name + ': error: unrecognized arguments: %s\n' % ' '.join(argv))
    argsParser.print_help()
    return None
  
  return args
  
def _Dump():
  Atta.logger.Log('*** Atta', level = LogLevel.DEBUG)
  Atta.logger.Log('Platform.platform = ' + platform.platform(), level = LogLevel.DEBUG)
  Atta.logger.Log('Platform.system = ' + platform.system(), level = LogLevel.DEBUG)
  Atta.logger.Log('Python.versionName = ' + platform.python_version(), level = LogLevel.DEBUG)
  Atta.logger.Log('Atta.versionName = ' + Atta.versionName, level = LogLevel.DEBUG)
  Atta.logger.Log('Atta.version = ' + str(Atta.version), level = LogLevel.DEBUG)
  Atta.logger.Log('Atta.dirName = ' + Atta.dirName, level = LogLevel.DEBUG)
  Atta.logger.Log('***', level = LogLevel.DEBUG)

def Main():
  minPythonVersion = '2.7.0'
  if int(platform.python_version().replace('.', '')) < int(minPythonVersion.replace('.', '')):
    print('Wrong version of Python. Requires {0}+ and {1} were detected.'.format(minPythonVersion, platform.python_version()))
    return 1

  Atta.dirName = os.path.dirname(os.path.realpath(sys.argv[0]))
  argv = sys.argv[1:]
  
  try:
    prop = Properties().Open(os.path.join(Atta.dirName, 'Atta.properties'))
    args = prop.Get('args', None)
    if args is not None:
      argv += args.split(' ')
  except:
    pass
  
  args = _ParseArgv(argv)
  if args is None:
    return 1
  
  if args.ll:
    Atta.logger.SetLevel(args.ll[0])

  if args.lc:
    __import__(OS.Path.RemoveExt(args.lc[0]))
    Atta.logger.SetClass(args.lc[0])
  
  _Dump()
  Atta.logger.Log("args = {0}".format(args), level = LogLevel.DEBUG)
  
  try:
    Project()._Run(os.environ, args.f[0], args.target)
    return 0
  
  except Exception, e:
    if args.scs or LogLevel.Get() <= LogLevel.VERBOSE:
      raise
    else:
      Atta.logger.Log(e, level = LogLevel.ERROR)
      return 1
  
  finally:
    pass
    
if __name__ == "__main__":
  sys.exit(Main())
