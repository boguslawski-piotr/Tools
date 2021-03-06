"""
Atta build module.

TODO: description
"""
import os

from atta import *

# python c:\python\tools\scripts\2to3.py -n -w -o atta3 atta >2to3.log

if Project is not None:
  Project.version.Configure(fileName = 'atta/version.py', format = Version.Formats.MMP)
  Project.vcs = Git()

  # Install all needed dependencies.
  packages = [
    {
    'repository': '.repositories.Http',
    'style'     : '.repositories.Styles.OnlyFileName',
    'url'       : 'http://prdownloads.sourceforge.net/cx-freeze',
    'package'   : 'cx_Freeze.tar.gz:4.3',
    #'fileNames' : 'cx_Freeze-4.3.tar.gz'
    },
    {
    'repository': '.repositories.PyPI',
    'package'   : 'Sphinx.tar.gz:1.1.3'
    }
  ]

  _, packages = Project.ResolveDependencies(packages)
  PyInstall(packages, siParams = '--user', failOnError = False, logOutput = (Atta.LogLevel() <= LogLevel.VERBOSE))

#------------------------------------------------------------------------------

class cleanDocs(Target):
  """ Clean auto generated documentation files."""
  def Run(self):
    Delete(DirSet(includes = ['docs/html', 'docs/modules*']), includeEmptyDirs = True)
    Delete(FileSet(includes = ['docs/*_user.rst', 'docs/*_dev.rst']), includeEmptyDirs = True)

class clean(Target):
  """ Clean all."""
  dependsOn = [cleanDocs]
  def Run(self):
    Delete(DirSet(includes = ['**/*build', '**/dist', 'tests/**/bin', 'examples/**/bin', 'tests/**/archive', '**/_test*']), includeEmptyDirs = True)
    Delete(['**/*.py?', '**/*.log', '**/*.class', '**/*.jar', '**/*.out', 'tests/test_Java'], includeEmptyDirs = True)

#------------------------------------------------------------------------------

import atta.loggers.Std as Std

class TestsLogger(Std.Logger):
  def __init__(self):
    open(os.path.join(Project.dirName, 'tests.log'), 'wb').close()

  def _PhysicalLog(self, msg):
    if msg:
      with open(os.path.join(Project.dirName, 'tests.log'), 'a+b') as f:
        f.write(msg + os.linesep)

class tests(Target):
  """ Run Atta tasks and targets tests."""
  def Run(self):
    listener = Atta.Logger().RegisterListener(TestsLogger)
    for fileName in FileSet(includes = 'tests/test_*.py', excludes = "**/test_exec_output.py"):
      self.Log('\nRunning project: ' + fileName)
      Project.RunProject(None, fileName, '')
    Atta.Logger().UnRegisterListener(listener)

#------------------------------------------------------------------------------

class unittests(Target):
  """ Run Atta unit tests."""
  def Run(self):
    from datetime import datetime
    Echo('\n\nSTARTED at: %s\n======================================================================\n\n' % datetime.today(),
          file = 'unittests.log', append = True)
    t = PyExec('-m', ['unittest', 'discover', '-v', '-p', '*', '-s', 'tests\unittest'], failOnError = False, useShell = False)
    Echo(t.output, file = 'unittests.log', append = True)
    if t.returnCode:
      raise AttaError(self, 'Unit tests are not performed correctly.')

#------------------------------------------------------------------------------

class makedocs(Target):
  """ Make Atta documentation.
  """
  dependsOn = [cleanDocs]

  def Run(self):
    Echo('Generating user automodules...')
    self.UserDocs()
    Echo('Generating developer automodules...')
    self.DevDocs()
    Echo('Running Sphinx...')
    self.Sphinx()

  def DevDocs(self):
    OS.MakeDirs('docs/modules')
    m = {}
    for fileName in FileSet('atta', includes = ['**/*.py'], excludes = ['**/__*', '**/*Test*', '**/templates/'], realPaths = False):
      fileName = OS.Path.RemoveExt(fileName)
      moduleName = fileName.replace(os.path.sep, '.')
      dirName, _ = os.path.split(fileName)
      if dirName:
        OS.MakeDirs(os.path.join('docs/modules', dirName))

      groupFileName = (dirName if len(dirName) > 0 else 'atta')
      groupDirName = os.path.join('modules', dirName).replace('\\', '/')
      m[groupFileName] = groupDirName

      Echo('  ' + fileName, level = LogLevel.VERBOSE)
      Echo(''':mod:`${name}`
-------------------------------------------------------------------------------

.. automodule:: ${fullName}
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:
    :member-order: bysource
''',
      name = moduleName,
      fullName = 'atta.' + moduleName,
      file = os.path.join('docs/modules', fileName) + '.rst',
      )

    devRefData2 = '''
.. toctree::
  :maxdepth: 1

'''
    for group in sorted(m.keys()):
      groupName = group[0].upper() + group[1:]
      groupName = groupName.replace('\\', '\\\\')
      groupData = groupName + '''
-------------------------------------------------------------------------------

.. toctree::
  :maxdepth: 4
  :glob:

  ''' + m[group] + '/*'
      groupFileName = group.replace('\\', '/').replace('/', '_') + '_dev.rst'
      Echo(groupData, file = os.path.join('docs', groupFileName))
      devRefData2 = devRefData2 + '  ' + OS.Path.RemoveExt(groupFileName) + '\n'
    Echo(devRefData2, file = 'docs/index_dev.rst')

  def UserDocs(self):
    m = {}
    ms = {}
    for fileName in FileSet('atta', includes = ['targets/**/*.py', 'tasks/**/*.py', 'tools/**/*.py', 'vcs/**/*.py'], excludes = ['**/__*', '**/*Test*', '**/templates/'], realPaths = False):
      group = fileName.split(os.path.sep)[0]
      subgroup = 'TODO'
      desc = ''
      usecases = ''
      with open(os.path.join('atta', fileName), 'r') as f:
        line = f.readline()
        if not line.startswith('"""') and not line.startswith("'''"):
          raise AttaError(self, 'ERROR: No documentation for: ' + fileName)
        line = line.replace("'''", "").strip()
        line = line.replace('"""', '').strip()
        if line == '.. no-user-reference:':
          continue
        line = line.replace(".. ", "").strip()
        w = line.split(':')
        if len(w) > 1:
          subgroup = w[0]
          del w[0]
        desc = w[0]
        if len(w) > 1:
          usecases = w[1].strip()
        else:
          Echo('WARNING: No use cases for: ' + fileName, level = LogLevel.WARNING)

      if group in m:
        if subgroup in m[group]:
          m[group][subgroup].append([desc, fileName, usecases])
        else:
          m[group][subgroup] = [[desc, fileName, usecases]]
      else:
        m[group] = { subgroup : [[desc, fileName, usecases]] }

    for i, group in enumerate(sorted(m.keys())):
      groupFileName = os.path.join('docs', group + '_user.rst')
      groupData = '''${groupName}\n===============================================================================\n'''
      Echo(groupFileName, level = LogLevel.VERBOSE)
      for subgroup in sorted(m[group]):
        outputFile = os.path.join('docs/modules_user/', group, subgroup)
        OS.MakeDirs(outputFile)
        groupData = (groupData + subgroup + '\n-------------------------------------------------------------------------------\n\n' +
                                            '.. toctree::\n  :glob:\n\n' +
                                            '  modules_user/${group}/' + subgroup + '/*\n\n'
                    )
        for doc in sorted(m[group][subgroup]):
          #print doc
          fileName = OS.Path.RemoveExt(doc[1])
          desc = doc[0]
          usecases = doc[2]
          if len(usecases) > 0:
            ucs = usecases
            usecases = ''
            for uc in ucs.split(','):
              usecases = usecases + '\n\n**Use cases:**\n\n  .. literalinclude:: ../../../../tests/test_''' + uc.strip() + '.py\n\n'
          moduleName = OS.Path.Ext(fileName.replace(os.path.sep, '.'), False)
          Echo('  ' + fileName, level = LogLevel.VERBOSE)
          Echo('''${moduleName} - ${desc}
-------------------------------------------------------------------------------

.. automodule:: ${fullName}
    :members:
    :undoc-members:
    :show-inheritance:
    :member-order: bysource
    ''' + usecases,
          moduleName = moduleName,
          desc = desc,
          fullName = 'atta.' + fileName.replace(os.path.sep, '.'),
          file = os.path.join(outputFile, moduleName) + '.rst',
          )

      mapGroupNames = { 'vcs' : 'Version Control'}
      if group in mapGroupNames:
        groupName = mapGroupNames[group]
      else:
        groupName = group.capitalize()
      ms[groupName] = group
      Echo(groupData,
            group = group,
            groupName = groupName,
            file = groupFileName)

    userRefData2 = '\n.. toctree::\n  :maxdepth: 1\n\n  Environment\n'
    for i, group in enumerate(sorted(ms.keys())):
      userRefData2 = userRefData2 + '  ' + ms[group] + '_user\n'
    Echo(userRefData2, file = 'docs/index_user.rst')

  def Sphinx(self):
    Project.env.chdir('docs')
    Exec('make', ['clean'], logOutput = False)
    Exec('make', ['html'], logOutput = (self.LogLevel() <= LogLevel.VERBOSE))

    # Show documentation
    if self.Env().get('SHOW'):
      Exec(os.path.join('html', 'index.html'), failOnError = False)

#------------------------------------------------------------------------------

class build(Target):
  #dependsOn = [makedocs]
  def Run(self):
    # Create Atta ... using cx_Freeze
    e = PyExec('buildexe', ['install_exe'], logOutput = (self.LogLevel() <= LogLevel.VERBOSE))
    Echo(e.output, file = 'buildexe.log', append = False)
    if self.LogLevel() > LogLevel.VERBOSE:
      Echo([l for l in e.output.split('\n') if l.lower().find('copying') < 0 and l.lower().find('creating') < 0])

    #
    from buildexeprops import installBaseDirName, installDirName, platformInstallDirName, archiveFileName
    zipFileName = os.path.join(installBaseDirName, archiveFileName)
    Zip(zipFileName, FileSet(platformInstallDirName, includes = '**/*'))
    Delete(installDirName, force = True)
    if OS.IsUnix():
      Delete(installBaseDirName + '/bin', force = True)

#------------------------------------------------------------------------------

class nextBuild(Target):
  dependsOn = [build]

  def Prepare(self):
    if Project.vcs:
      if not Project.vcs.IsWorkingDirectoryClean():
        raise AttaError(self, 'Working directory is not clean.')
    return True

  def Run(self):
    if Project.vcs:
      Project.vcs.SetTag('v' + Atta.version)
      Project.version.NextPatch()
      Project.vcs.CommitAndPublishAllChanges('Next build number', remotes = 'origin sf')
