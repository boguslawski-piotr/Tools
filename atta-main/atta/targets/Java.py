'''
Java Target

TODO: description
'''
import shutil
import os

from atta import *

# Settings

def Setup(srcBaseDir = 'src', buildBaseDir = 'build', installBaseDir = 'bin', deployBaseDir = 'archive', mainClass = 'main'):
  project = GetProject()
  #print 'in Java.setup'
  #print project
  
  project.srcBaseDir = srcBaseDir
  '''TODO: description'''
  
  project.buildBaseDir = buildBaseDir
  '''TODO: description'''
  
  project.installBaseDir = installBaseDir
  '''TODO: description'''
  
  project.deployBaseDir = deployBaseDir
  '''TODO: description'''
  
  
  project.javaDirs = [project.srcBaseDir + '/main/java']
  '''TODO: description'''
  
  project.javaTestDirs = [project.srcBaseDir + '/test/java']
  '''TODO: description'''
  
  project.classDirs = [project.buildBaseDir + '/classes/main']
  '''TODO: description'''
  
  project.classTestDirs = [project.buildBaseDir + '/classes/test']
  '''TODO: description'''
  
  
  project.javacClassPath = []
  '''TODO: description'''
  
  project.javacSourcePath = []
  '''TODO: description'''
  
  project.debug = False
  '''TODO: description'''
  
  project.debugLevel = None
  '''TODO: description'''
  
  
  project.packageNameFormat = '{0}-{1}'
  '''TODO: description
  {0} - project name
  {1} - project version name
  '''
  
  project.packageName = []
  '''result package file name set in package target TODO: description'''
  
  project.packageAdditionalFiles = []
  '''TODO: description'''
  
  project.javaMainClass = mainClass
  '''TODO: description'''

  project.defaultTarget = 'help'

  project.targetsMap['help']    = 'atta.targets.Java.help'
  project.targetsMap['clean']   = 'atta.targets.Java.clean'
  project.targetsMap['prepare'] = 'atta.targets.Java.prepare'
  project.targetsMap['compile'] = 'atta.targets.Java.compile'
  project.targetsMap['package'] = 'atta.targets.Java.package'
  project.targetsMap['install'] = 'atta.targets.Java.install'
  project.targetsMap['deploy']  = 'atta.targets.Java.deploy'
  
# Tools

# Targets

class prepareEnvironment(Target):
  def Run(self):
    # Create the necessary directories.
    project = GetProject()
    create = False
    for classDir in project.classDirs:
      if not os.path.exists(classDir):
        create = True
        break
    if create:
      Echo('Creating directories:')
      for classDir in project.classDirs:
        Echo(os.path.normpath(classDir))
      OS.MakeDirs(project.classDirs)

class prepare(Target):
  dependsOn = [prepareEnvironment]
  def Run(self):
    project = GetProject()
    packages = project.ResolveDependencies()
    if packages is not None:
      project.javacClassPath.extend(packages)
  
class clean(Target):
  def Run(self):
    project = GetProject()
    Echo('Deleting directory: ' + os.path.normpath(project.buildBaseDir))
    shutil.rmtree(project.buildBaseDir, True)
    Echo('Deleting directory: ' + os.path.normpath(project.installBaseDir))
    shutil.rmtree(project.installBaseDir, True)

class compile(Target):
  dependsOn = [prepare]
  def Run(self):
    project = GetProject()
    i = 0
    for srcDir in project.javaDirs:
      if not project.classDirs[i] in project.javacClassPath:
        project.javacClassPath.append(project.classDirs[i])
      
      Javac([srcDir], 
            project.classDirs[i], 
            classPath = project.javacClassPath,
            sourcePath = project.javacSourcePath, 
            debug = project.debug, 
            debugLevel = project.debugLevel)
      
      if not OS.Path.HasWildcards(srcDir):
        if not srcDir in project.javacSourcePath:
          project.javacSourcePath.append(srcDir)
      
      if i < len(project.classDirs) - 1:
        i += 1
    
class package(Target):
  dependsOn = [compile]
  def Run(self):
    # Create jar file.
    project = GetProject()
    classDirs = project.classDirs[:]
    classDirs.extend(project.packageAdditionalFiles)
    packageName = os.path.join(project.buildBaseDir, self.PackageName()) + '.jar'
    Jar(packageName, 
        classDirs, 
        self.Manifest(),
        update = False)
    project.packageName = packageName
  
  def Manifest(self):
    # Create basic manifest.
    project = GetProject()
    manifest = {
                'Implementation-Title'  : project.name,
                'Implementation-Version': project.versionName,
                'Main-Class'            : project.javaMainClass,
               }
    return manifest
  
  def PackageName(self):
    # Create package name.
    project = GetProject()
    packageName = project.name
    if len(packageName) <= 0:
      raise AttaError(self, 'Project.name is not set.')
    if len(project.versionName) > 0:
      packageName = project.packageNameFormat.format(packageName, project.versionName)
    return packageName
   
class install(Target):
  '''TODO: Buduje caly projekt i umieszcza wszystko co potrzebne do jego uruchomienia w bin (default)'''
  dependsOn = [package]
  def Run(self):
    Echo('Installing into: ' + os.path.normpath(GetProject().installBaseDir))
    print GetProject().javacClassPath

class deploy(Target):
  '''TODO: Wysyla do roznych (konfiguracja) repozytoriow.
  Zwieksza numer builda.
  '''
  dependsOn = [install]
  def Run(self):
    Echo('Deplyoing into: ')
    
#------------------------------------------------------------------------------ 

class help(Target):
  def Run(self):
    Echo('Java help...')
        