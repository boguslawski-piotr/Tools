#!/usr/bin/python
'''
Atta main
'''
import platform
import sys
import os

from atta import Atta, LogLevel, Properties, Javac, OS
import atta.Project
import atta.Dict

def _ParseArgv(argv):
  import argparse

  argsParser = argparse.ArgumentParser(
    prog = Atta.name,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = Atta.name
                  + ' v' + Atta.version
                  + os.linesep
                  + Atta.description,
    epilog = 'Bugs, comments and suggestions please report on page\nhttps://github.com/boguslawski-piotr/Atta/issues'
  )

  buildGroup = argsParser.add_argument_group('build')
  buildGroup.add_argument(
    'target', nargs = '*', default = '',
    help = ''
  )
  buildGroup.add_argument(
    '-f', nargs = 1, default = [atta.Dict.defaultBuildFileName], metavar = 'file',
    help = 'use given buildfile'
  )

  paramGroup = argsParser.add_argument_group('parameters')
  paramGroup.add_argument(
    '-D', action = 'append', metavar = 'name=value',
    help = "insert the 'value' to the list of environment variables (accessible through Project.env) under the name 'name' (the name is case-insensitive)"
  )

  tasksGroup = argsParser.add_argument_group('tasks')
  tasksGroup.add_argument(
    '-javac', nargs = 1, metavar = 'class',
    help = 'use given class as default Java compiler (class must implements IJavaCompiler)'
  )
  tasksGroup.add_argument(
    '-javarc', nargs = 1, metavar = 'class',
    help = 'use given class to implement the Javac.RequiresCompile (class must implements IRequiresCompileStrategy)'
  )

  logGroup = argsParser.add_argument_group('logging')
  logGroup.add_argument(
    '-d', action = 'store_true',
    help = 'set debug mode (shortcut for -ll 0)')
  logGroup.add_argument(
    '-v', action = 'store_true',
    help = 'set verbose mode (shortcut for -ll 1)')
  logGroup.add_argument(
    '-q', action = 'store_true',
    help = 'be quiet (shortcut for -ll 3)')
  logGroup.add_argument(
    '-ll', nargs = 1, metavar = atta.Dict.paramLevel, type = int, choices = [0, 1, 2, 3, 4],
    help = 'set the log level to the one of: %(choices)s'
  )
  logGroup.add_argument(
    '-lm', nargs = 1, metavar = 'module',
    help = 'use given module with Logger class as logger (Logger must implements ILogger interface)'
  )
  logGroup.add_argument(
    '-llc', action = 'append', metavar = 'class',
    help = 'use given class as log listener (class must implements ILogger interface and you can specify more than one listener)'
  )
  logGroup.add_argument(
    '-scs', action = 'store_true',
    help = 'show call stack (traceback) on error')

  args, argv = argsParser.parse_known_args(argv)
  if argv:
    print(Atta.name + ': error: unrecognized arguments: %s\n' % ' '.join(argv))
    argsParser.print_help()
    return None

  return args

def _Dump():
  Atta.Log('*** Atta', level = LogLevel.DEBUG)
  Atta.Log('Platform.platform = ' + platform.platform(), level = LogLevel.DEBUG)
  Atta.Log('Platform.system = ' + platform.system(), level = LogLevel.DEBUG)
  Atta.Log('Python.version = ' + platform.python_version(), level = LogLevel.DEBUG)
  Atta.Log('Atta.version = ' + Atta.version, level = LogLevel.DEBUG)
  Atta.Log('Atta.version = ' + str(Atta.version), level = LogLevel.DEBUG)
  Atta.Log('Atta.dirName = ' + Atta.dirName, level = LogLevel.DEBUG)
  Atta.Log('***', level = LogLevel.DEBUG)

def Main():
  # Setup environment
  minPythonVersion = '2.7.0'
  if int(platform.python_version().replace('.', '')) < int(minPythonVersion.replace('.', '')):
    print('Wrong version of Python. Requires {0}+ and {1} were detected.'.format(minPythonVersion, platform.python_version()))
    return 1

  Atta.dirName = os.path.dirname(os.path.realpath(sys.argv[0]))
  argv = sys.argv[1:]
  environ = os.environ

  # Load settings

  try:
    # TODO: szukac atta.properties w: Atta dir, user dir and project dir (nowe zastepuja stare)
    Atta._SetProps(Properties.Open(os.path.join(Atta.dirName, 'atta.properties')))

    args = Atta.Props().Get('args', None)
    if args is not None:
      argv += args.split(' ')

  except:
    pass

  # Parse arguments

  args = _ParseArgv(argv)
  if args is None:
    return 1

  # Handle arguments

  if args.D:
    for D in args.D:
      try:
        D = D.split('=')
        name = D[0]
        value = '1' if len(D) <= 1 else D[1]
        environ[name] = value
      except:
        pass

  if args.javac:
    Javac.SetDefaultCompilerImpl(args.javac[0])
  if args.javarc:
    Javac.SetDefaultRequiresCompileImpl(args.javarc[0])

  if args.ll:
    Atta.Logger().SetLevel(args.ll[0])
  if args.d:
    Atta.Logger().SetLevel(LogLevel.DEBUG)
  if args.v:
    Atta.Logger().SetLevel(LogLevel.VERBOSE)
  if args.q:
    Atta.Logger().SetLevel(LogLevel.WARNING)
  if args.lm:
    __import__(args.lm[0])
    Atta.Logger().SetImpl(args.lm[0] + '.Logger')
  if args.llc:
    for llc in args.llc:
      __import__(OS.Path.RemoveExt(llc))
      Atta.Logger().RegisterListener(llc)

  _Dump()
  Atta.Log("args = {0}".format(args), level = LogLevel.DEBUG)
  Atta.Log('***', level = LogLevel.DEBUG)

  # Run project

  try:
    atta.Project.Project()._Run(environ, args.f[0], args.target)
    return 0

  except Exception as e:
    if args.scs or Atta.LogLevel() <= LogLevel.VERBOSE:
      import traceback
      exc_type, exc_value, exc_traceback = sys.exc_info()
      lines = traceback.extract_tb(exc_traceback)
      lines = lines[-5:] # only last five
      for line in lines:
        print('%s: %d' % (line[0], line[1]))
        print('  %s' % line[3])
      print('')
      for line in traceback.format_exception_only(exc_type, exc_value):
        print(line)
    else:
      Atta.Log(e, level = LogLevel.ERROR)
    return 1

  finally:
    pass

if __name__ == "__main__":
  sys.exit(Main())
