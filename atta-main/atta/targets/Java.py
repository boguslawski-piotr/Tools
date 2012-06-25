'''
Java Target

TODO: description
'''
from atta import *

import shutil
import os

if Project is not None:
  if hasattr(Project, 'targetsMap'):
    Project.targetsMap['help']    = 'atta.targets.Java.help'
    Project.targetsMap['clean']   = 'atta.targets.Java.clean'
    Project.targetsMap['compile'] = 'atta.targets.Java.compile'
    Project.targetsMap['package'] = 'atta.targets.Java.package'
    Project.targetsMap['install'] = 'atta.targets.Java.install'
    
    Project.defaultTarget = 'help'

# Settings

srcBaseDir = 'src'

buildBaseDir = 'build'

classBaseDir = buildBaseDir + '/classes'

installBaseDir = 'bin'

externalLibsBaseDir = 'libs'


srcDirs = [srcBaseDir + '/main/java']
'''TODO: description'''

srcTestDirs = [srcBaseDir + '/test/java']
'''TODO: description'''

classDirs = [classBaseDir + '/main']
'''TODO: description'''

classTestDirs = [classBaseDir + '/test']
'''TODO: description'''


classPath = []
'''TODO: description'''

sourcePath = []
'''TODO: description'''

packageNameFormat = '{0}-{1}'
'''TODO: description'''

debug = False
'''TODO: description'''

debugLevel = ''
'''TODO: description'''

mainClassName = ''
'''TODO: description'''

# Tools

# Targets

class prepare(Target):
  def Run(self):
    Echo('Creating directories:')
    for classDir in classDirs:
      Echo(os.path.realpath(classDir))
    OS.MakeDirs(classDirs)

class clean(Target):
  def Run(self):
    Echo('Deleting directory: ' + os.path.realpath(buildBaseDir))
    shutil.rmtree(buildBaseDir, True)
    Echo('Deleting directory: ' + os.path.realpath(installBaseDir))
    shutil.rmtree(installBaseDir, True)

class compile(Target):
  DependsOn = [prepare]
  def Run(self):
    i = 0
    for srcDir in srcDirs:
      if not classDirs[i] in classPath:
        classPath.append(classDirs[i])
      Javac([srcDir], 
            classDirs[i], 
            classPath = classPath,
            sourcePath = sourcePath, 
            debug = debug, 
            debugLevel = debugLevel)
      if i < len(classDirs) - 1:
        i += 1
    
class package(Target):
  DependsOn = [compile]
  def Run(self):
    # Create package name.
    packageName = Project.name
    if len(packageName) <= 0:
      raise SystemError('Project.name is not set.')
    if len(Project.versionName) > 0:
      packageName = packageNameFormat.format(packageName, Project.versionName) 
    
    # Create basic manifest.
    manifest = {
                'Implementation-Title'  : Project.name,
                'Implementation-Version': Project.versionName,
                'Main-Class'            : mainClassName,
               }
    
    # Create jar file.
    Jar(os.path.join(buildBaseDir, packageName) + '.jar', 
        classDirs, 
        manifest)

class install(Target):
  DependsOn = [package]
  def Run(self):
    Echo('Installing into: ' + os.path.realpath(installBaseDir))
    
#------------------------------------------------------------------------------ 

class help(Target):
  def Run(self):
    Echo('Java help...')
        