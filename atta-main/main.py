#!/usr/bin/python

## \brief  pyant main
#  \author Piotr Boguslawski (boguslawski.piotr@gmail.com)

import sys
import importlib

from pyant.BaseClasses import *
from pyant.Log import *
from pyant.Properties import Properties
from pyant.OS import *

#===============================================================================
# Consts
#===============================================================================

defaultBuildFile = 'build.py'

#===============================================================================
# Environment & parameters
#===============================================================================

Program.dirName = os.path.dirname(os.path.realpath(sys.argv[0]))

# TODO: read pyant.properties
#p = Properties()
Program.version = '0.1'

import argparse

argsParser = argparse.ArgumentParser(
  prog = Program.name,
  formatter_class=argparse.RawDescriptionHelpFormatter,
  description = 
  'pyant v' + Program.version + 
  '''
  The Ant in Python :)''',
  epilog = 
    'Bugs found, suggestions for improvements, etc. \nplease send to: boguslawski.piotr@gmail.com'
)

argsParser.add_argument(
  'target', nargs = '*', default = '',
  help = ''
)
argsParser.add_argument(
  '-f', nargs = 1, default = [defaultBuildFile], metavar = 'file',
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

args = argsParser.parse_args()
Program.args = args

if args.ll:
  logLevel = args.ll[0]
if args.lc:
  script = 'import ' + args.lc[0] + \
           '\nLoggerBridge.LoggerClass = ' + args.lc[0] + '.Logger\n'
  exec(script)
else:
  from pyant.StdLogger import Logger
  LoggerBridge.LoggerClass = Logger
  
Project.dirName = os.path.normpath(os.path.realpath(os.path.dirname(args.f[0])))
Project.fileName = os.path.join(Project.dirName, RemoveExt(os.path.basename(args.f[0])) + '.py')

Env.chdir(Project.dirName)
Env.SetAttrsFromSystem()

Program.Dump();
Env.Dump();
Project.Dump();
Log(' ', level=LogLevel.DEBUG)

#===============================================================================
# Main 
#===============================================================================

try:
  build = Build()
  build.Start()
  
  buildFileName = os.path.join(Project.dirName, Project.fileName)
  Log('Buildfile: ' + buildFileName)
  if not os.path.exists(buildFileName):
    raise IOError(os.errno.ENOENT, 'Buildfile: {0} does not exists!'.format(buildFileName))
  
  sys.path.append(Project.dirName)
  buildFile = importlib.import_module(RemoveExt(os.path.basename(Project.fileName)))
  
#  buildFile = open(Project.buildFile, 'r')
#  script = ''
#  for line in buildFile.readlines():
#    script = script + line + os.linesep
#  buildFile.close()
#  script = build.ParseScript(script)
#  exec(script)
  
  if len(args.target) <= 0 or len(args.target[0]) <= 0:
    args.target = [Project.defaultTarget]
    if len(args.target) <= 0 or len(args.target[0]) <= 0:
      build.End(Build.SUCCESSFUL);
      sys.exit(0)
  
  script = ''
  for targetName in args.target:
    script = script + '\nbuild.Run(buildFile.' + targetName + ')'
#    script = script + '\nbuild.Run(' + targetName + ')'
  script = build.ParseScript(script)
  exec(script)

except ImportError, e:
  build.End(Build.FAILED, e)
  Log(e, level = LogLevel.ERROR)
  sys.exit(1)
except Exception, e:
  build.End(Build.FAILED, e)
  if logLevel == LogLevel.DEBUG:
    raise
  else:
    Log(e, level = LogLevel.ERROR)
    sys.exit(1)

build.End(Build.SUCCESSFUL)
sys.exit(0)