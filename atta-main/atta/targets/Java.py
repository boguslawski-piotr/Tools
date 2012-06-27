'''
Java Target

TODO: description
'''
import shutil
import os
import stat

from atta import *

class ProjectType:
  consoleApp = 'capp'
  # capp, jar, war, ...
  
class Setup:
  '''TODO: description'''
  def __init__(self, type_ = ProjectType.consoleApp, **tparams):
    '''TODO: description'''
    project = GetProject()
    #print 'in Java.setup'
    #print project
    
    project.type_ = type_
    '''TODO: description
    available values: see ProjectType
    '''
    
    project.srcBaseDir = tparams.get('srcBaseDir', 'src')
    '''TODO: description'''
    
    project.buildBaseDir = tparams.get('buildBaseDir', 'build')
    '''TODO: description'''
    
    if project.type_ == ProjectType.consoleApp:
      defInstallBaseDir = 'bin'
    else:
      defInstallBaseDir = 'lib'
    project.installBaseDir = tparams.get('installBaseDir', defInstallBaseDir)
    '''TODO: description'''
    
    project.deployBaseDir = tparams.get('deployBaseDir', 'archive')
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
    
    project.packageName = ''
    '''result package file name set in package target TODO: description'''
    
    project.packageAdditionalFiles = []
    '''TODO: description'''
    
    project.javaClassPath = []
    '''TODO: description'''
    
    project.javaMainClass = tparams.get('mainClass', 'main')
    '''TODO: description'''
  
    # internal settings
    
    project.defaultTarget = 'help'
  
    project.targetsMap['help']    = 'atta.targets.Java.help'
    project.targetsMap['clean']   = 'atta.targets.Java.clean'
    project.targetsMap['prepare'] = 'atta.targets.Java.prepare'
    project.targetsMap['compile'] = 'atta.targets.Java.compile'
    project.targetsMap['package'] = 'atta.targets.Java.package'
    project.targetsMap['install'] = 'atta.targets.Java.install'
    project.targetsMap['deploy']  = 'atta.targets.Java.deploy'
  
#------------------------------------------------------------------------------ 

class prepare(Target):
  '''TODO: description'''
  def Run(self):
    '''TODO: description'''
    self.PrepareEnvironment()
    self.ResolveDependencies()
    
  def PrepareEnvironment(self):
    '''Create the necessary directories.'''
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
  
  def ResolveDependencies(self):
    '''TODO: description'''
    project = GetProject()
    packages = project.ResolveDependencies()
    if packages is not None:
      project.javacClassPath.extend(packages)

#------------------------------------------------------------------------------ 

class compile(Target):
  '''TODO: description'''
  dependsOn = ['prepare']

  def Run(self):
    '''TODO: description'''
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
    
#------------------------------------------------------------------------------ 

class package(Target):
  '''TODO: description'''
  dependsOn = ['compile']
  
  def Run(self):
    '''Create package.'''
    project = GetProject()
    classDirs = project.classDirs[:]
    self.ExtendClassDirs(classDirs)
    project.packageName = os.path.join(project.buildBaseDir, self.GetPackageName())
    Jar(project.packageName, classDirs, self.GetManifest())
  
  def ExtendClassDirs(self, classDirs):
    '''TODO: description'''
    classDirs.extend(GetProject().packageAdditionalFiles)
    
  def GetManifest(self):
    '''Creates basic manifest.'''
    project = GetProject()
    manifest = {
                'Implementation-Title'  : project.name,
                'Implementation-Version': project.versionName,
                'Main-Class'            : project.javaMainClass,
               }
    return manifest
  
  def GetPackageName(self):
    '''Creates package (base) file name.'''
    project = GetProject()
    packageName = project.name
    if len(packageName) <= 0:
      raise AttaError(self, 'Project.name is not set.')
    if len(project.versionName) > 0:
      packageName = project.packageNameFormat.format(packageName, project.versionName)
    return packageName + '.jar'
   
#------------------------------------------------------------------------------ 

class install(Target):
  '''TODO: Buduje caly projekt i umieszcza wszystko co potrzebne do jego uruchomienia w bin (default)'''
  dependsOn = ['package']
  
  def Run(self):
    '''TODO: description'''
    project = GetProject()
    javaClassPath = []

    # Create install directory (if needed).
    if not os.path.exists(project.installBaseDir):
      Echo('Creating directory: ' + os.path.normpath(project.installBaseDir))
      OS.MakeDirs(project.installBaseDir)
    
    self.CopyDependencies(javaClassPath)
    self.CopyPackage(javaClassPath)
    
    if project.type_ == ProjectType.consoleApp:
      self.CreateStartupScripts(javaClassPath)
      
  def CopyDependencies(self, javaClassPath):
    '''Copy dependencies. TODO: more...'''
    project = GetProject()
    for packageName in project.javacClassPath:
      if os.path.exists(packageName) and not os.path.isdir(packageName):
        destFileName = os.path.join(project.installBaseDir, os.path.basename(packageName))
        if OS.CopyFileIfDiffrent(packageName, destFileName, useHash = True):
          Echo('Installed: ' + destFileName)
        javaClassPath.append(os.path.basename(packageName))
  
  def CopyPackage(self, javaClassPath):
    '''Copy package. TODO: more... '''
    project = GetProject()
    destFileName = os.path.join(project.installBaseDir, os.path.basename(project.packageName))
    if OS.CopyFileIfDiffrent(project.packageName, destFileName, useHash = True):
      Echo('Installed: ' + destFileName)
    javaClassPath.insert(0, os.path.basename(project.packageName))  # Inserted at the beginning, for the case if 
                                                                    # other libraries contain class: project.javaMainClass.
  
  def CreateStartupScripts(self, javaClassPath):
    '''Create shell scripts. TODO: more...'''
    project = GetProject()
    javaClassPathStr = os.pathsep + '${projectHome}/'
    javaClassPathStr = javaClassPathStr + javaClassPathStr.join(javaClassPath)
    javaClassPathStr = os.path.normpath(javaClassPathStr)
    projectNameInScript = project.name.upper().replace(' ', '_')
    
    # windows
    with open(self.GetWinStartupScriptTmplFileName(), 'rb') as f:
      scriptName = os.path.join(project.installBaseDir, project.name + '.bat')
      Echo(f, file = scriptName, force = True,
           projectName = projectNameInScript,
           projectHome = '%' + projectNameInScript + '_HOME%',
           mainClass   = project.javaMainClass,
           classPath   = javaClassPathStr)
    # unix family
    with open(self.GetUnixStartupScriptTmplFileName(), 'rb') as f:
      scriptName = os.path.join(project.installBaseDir, project.name)
      Echo(f, file = scriptName, force = True,
           projectName = projectNameInScript,
           projectHome = '$' + projectNameInScript + '_HOME',
           mainClass   = project.javaMainClass,
           classPath   = javaClassPathStr.replace('\\', '/').replace(';', ':')) 
      os.chmod(scriptName, stat.S_IEXEC)
    
  def GetWinStartupScriptTmplFileName(self):
    '''TODO: description'''
    return Atta.dirName + '/atta/templates/JavaConsoleApp.bat.tmpl'
  
  def GetUnixStartupScriptTmplFileName(self):
    '''TODO: description'''
    return Atta.dirName + '/atta/templates/JavaConsoleApp.sh.tmpl'
  
#------------------------------------------------------------------------------ 

class deploy(Target):
  '''TODO: Wysyla do roznych (konfiguracja) repozytoriow.
  Zwieksza numer builda.
  '''
  dependsOn = ['install']

  def Run(self):
    '''TODO: description'''
    Echo('Deplyoing into: ')
    
#------------------------------------------------------------------------------ 

class clean(Target):
  '''TODO: description'''
  def Run(self):
    project = GetProject()
    Echo('Deleting directory: ' + os.path.normpath(project.buildBaseDir))
    shutil.rmtree(project.buildBaseDir, True)
    Echo('Deleting directory: ' + os.path.normpath(project.installBaseDir))
    shutil.rmtree(project.installBaseDir, True)

#------------------------------------------------------------------------------ 

class help(Target):
  '''TODO: description'''
  def Run(self):
    Echo('Java help...')
        