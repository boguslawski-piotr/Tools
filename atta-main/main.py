#!/usr/bin/python
"""
Atta main
"""
import platform
import sys
import os
from logilab.common.test.unittest_interface import D

from atta import Atta, LogLevel, Properties, OS, Dict

def _ParseArgv(argv):
  import argparse

  argsParser = argparse.ArgumentParser(
    prog = Atta.name,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    description = Atta.name
                  + ' v' + Atta.version
                  + os.linesep
                  + Atta.description,
    epilog = '''
More options are available in the file ''' + Dict.attaPropsFileName + '''
which is searched in the following locations and in such order:

  the Atta directory,
  the user's home directory,
  the directory of the project.

Options read later override previously set.
Options from the command line overrides all others.

Bugs, comments and suggestions please report on page\nhttps://github.com/boguslawski-piotr/Atta/issues
'''
  )

  buildGroup = argsParser.add_argument_group('build')
  buildGroup.add_argument(
    'target', nargs = '*', default = '',
    help = ''
  )
  buildGroup.add_argument(
    '-f', nargs = 1, default = [Dict.defaultBuildFileName], metavar = 'file',
    help = 'use given buildfile'
  )

  paramGroup = argsParser.add_argument_group('parameters')
  paramGroup.add_argument(
    '-D', action = 'append', metavar = 'name=value',
    help = "insert the 'value' to the list of environment variables (accessible through Project.env) under the name 'name' always converted to uppercase."
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
    '-scs', action = 'store_true',
    help = 'show call stack (traceback) on error')

  args, argv = argsParser.parse_known_args(argv)
  if argv:
    print(Atta.name + ': error: unrecognized arguments: %s\n' % ' '.join(argv))
    argsParser.print_help()
    return None

  return args

def _PutArgsIntoProps(args, props):
  if args.D:
    for D in args.D:
      try:
        D = D.split('=')
        props[D[0]] = '1' if len(D) <= 1 else D[1]
      except Exception:
        continue

  if args.scs: props['scs'] = args.scs
  if args.d: props['d'] = args.d
  if args.v: props['v'] = args.v
  if args.q: props['q'] = args.q

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

  # Load settings (part 1).

  try:
    # Load the settings from the Atta directory (global settings)
    # and the user's home directory (user settings).
    # User settings override the global settings.
    gprops = None
    uprops = None
    try: gprops = Properties.Open(os.path.join(Atta.dirName, Dict.attaPropsFileName), True)
    except Exception: pass
    try: uprops = Properties.Open(os.path.join(os.path.expanduser('~'), Dict.attaPropsFileName), True)
    except Exception: pass
    props = gprops.ItemsAsDict()
    if uprops:
      props.update(uprops.ItemsAsDict())
    Atta._SetProps(props)
  except Exception:
    pass

  # Parse command line arguments.

  args = _ParseArgv(argv)
  if args is None:
    return 1

  buildFileName = args.f[0]

  # Load settings (part 2).

  try:
    # Load the settings from build directory (project settings).
    # Project settings override the global and user settings.
    buildDirName = os.path.dirname(os.path.realpath(buildFileName))
    if buildDirName != Atta.dirName:
      pprops = Properties.Open(os.path.join(buildDirName, Dict.attaPropsFileName), True)
      Atta.Props().update(pprops.ItemsAsDict())
  except Exception:
    pass

  # Command line settings override the global, user and project settings.

  props = Atta.Props()
  _PutArgsIntoProps(args, props)

  # Handle settings.

  def Bool(v):
    if isinstance(v, basestring):
      v = v.lower()
      return v == '1' or v == Dict.true or v == Dict.yes
    return bool(v)

  # -Dname=value definitions
  for N, V in props.items():
    if N.startswith('D'):
      environ[N[1:]] = '1' if len(V) <= 0 else V

  Atta.Logger().SetLevel(props.get('ll', LogLevel.Default()))

  if Bool(props.get('d')):
    Atta.Logger().SetLevel(LogLevel.DEBUG)
  if Bool(props.get('v')):
    Atta.Logger().SetLevel(LogLevel.VERBOSE)
  if Bool(props.get('q')):
    Atta.Logger().SetLevel(LogLevel.WARNING)

  lc = props.get('lc')
  if lc:
    __import__(OS.Path.RemoveExt(lc))
    Atta.Logger().SetImpl(lc)

  llc = OS.Path.AsList(props.get('llc'), ',')
  for c in llc:
    __import__(OS.Path.RemoveExt(c))
    Atta.Logger().RegisterListener(c)

  javac = props.get('javac')
  if javac:
    from atta.tasks.Javac import Javac
    Javac.SetDefaultCompilerImpl(javac)
  javarc = props.get('javarc')
  if javarc:
    from atta.tasks.Javac import Javac
    Javac.SetDefaultRequiresCompileImpl(javarc)

  _Dump()
  Atta.Log("args = {0}".format(args), level = LogLevel.DEBUG)
  Atta.Log('***', level = LogLevel.DEBUG)

  # Run project

  try:
    from atta.Project import Project
    Project()._Run(environ, buildFileName, args.target)
    return 0

  except Exception as E:
    if props.get('scs') or Atta.LogLevel() <= LogLevel.VERBOSE:
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
      Atta.Log(E, level = LogLevel.ERROR)
    return 1

if __name__ == "__main__":
  sys.exit(Main())
