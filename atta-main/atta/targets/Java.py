'''.. Software projects: Builds Java projects

TODO: description
'''
import os
import stat

from ..repositories.Package import PackageId
from ..repositories import Styles
from .. import Dict

from atta import *

class ProjectType:
  app = 'app'
  jar = Dict.jar
  war = Dict.war
  
class Setup:
  '''TODO: description'''
  def __init__(self, type = ProjectType.app, **tparams):
    '''TODO: description'''
    project = GetProject()
    
    if not hasattr(project, 'groupId'):
      project.groupId = project.name
      
    project.type = type
    '''TODO: description
    available values: see ProjectType
    '''
    
    project.srcBaseDir = tparams.get('srcBaseDir', 'src')
    '''TODO: description'''
    
    project.buildBaseDir = tparams.get('buildBaseDir', 'build')
    '''TODO: description'''
    
    if project.type == ProjectType.app:
      defInstallBaseDir = 'bin'
    else:
      defInstallBaseDir = 'lib'
    project.installBaseDir = tparams.get('installBaseDir', defInstallBaseDir)
    '''TODO: description'''
    
    
    project.javaDirs = [project.srcBaseDir + '/main/java']
    '''TODO: description'''
    
    project.javaTestDirs = [project.srcBaseDir + '/test/java']
    '''TODO: description'''
    
    project.classDirs = [project.buildBaseDir + '/classes/main']
    '''TODO: description'''
    
    project.classTestDirs = [project.buildBaseDir + '/classes/test']
    '''TODO: description'''
    
    
    project.javacClassPathAllowedExts = ['class', 'jar', 'war']
    '''TODO: description'''
    
    project.javacClassPath = []
    '''TODO: description'''
    
    project.javacSourcePath = []
    '''TODO: description'''
    
    project.debug = False
    '''TODO: description'''
    
    project.debugLevel = None
    '''TODO: description'''
    
    
    project.packageNameStyle = Styles.Maven
    '''TODO: description'''
    
    if project.type == ProjectType.app:
      project.packageExt = Dict.jar
    else:
      project.packageExt = project.type

    project.packageName = ''
    '''result package file name set in package target TODO: description'''
    
    project.packageAdditionalFiles = []
    '''TODO: description'''
    
    
    project.javaMainClass = tparams.get('mainClass', 'main')
    '''TODO: description'''

    
    project.installAdditionalFiles = []
    '''TODO: description'''

    project.installedFiles = []
    '''TODO: description'''

    project.neededPackages = []
    '''TODO: description'''
    
    
    project.deployedFiles = []
    '''TODO: description'''
    
    # internal settings
    
    project.defaultTarget = 'help'
  
    project.targetsMap['prepare'] = 'atta.targets.Java.prepare'
    project.targetsMap['compile'] = 'atta.targets.Java.compile'
    project.targetsMap['package'] = 'atta.targets.Java.package'
    project.targetsMap['install'] = 'atta.targets.Java.install'
    project.targetsMap['deploy']  = 'atta.targets.Java.deploy'
    project.targetsMap['clean']   = 'atta.targets.Java.clean'
    project.targetsMap['help']    = 'atta.targets.Java.help'
  
#------------------------------------------------------------------------------ 

def ResolveDependencies(scope):
  '''TODO: description'''
  project = GetProject()
  files, packages = project.ResolveDependencies(scope = scope, returnPackages = True)
  
  result = []
  if files is not None:
    # Leave only the files that make sense for the Java compiler or/and Java runtime.
    for p in files:
      append = os.path.isdir(p)
      if not append:
        append = OS.Path.Ext(p) in project.javacClassPathAllowedExts
      if append:
        result.append(p)
  
  if packages != None:
    project.neededPackages += packages
    
  return result

#------------------------------------------------------------------------------ 

class prepare(Target):
  '''TODO: description'''
  def Run(self):
    '''TODO: description'''
    self.PrepareEnvironment()
    
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
        Echo('  ' + os.path.normpath(classDir))
      OS.MakeDirs(project.classDirs)
  
#------------------------------------------------------------------------------ 

class compile(Target):
  '''TODO: description'''
  dependsOn = ['prepare']

  def Run(self):
    '''TODO: description'''
    project = GetProject()
    self.ResolveDependencies()
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

  def ResolveDependencies(self):
    '''TODO: description'''
    project = GetProject()
    project.javacClassPath += ResolveDependencies(scope = Dict.Scopes.compile)
    
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
                'Implementation-Version': str(project.version),
                'Main-Class'            : project.javaMainClass,
               }
    return manifest
  
  def GetPackageName(self):
    '''Creates package (base) file name.'''
    project = GetProject()
    if len(project.name) <= 0:
      raise AttaError(self, Dict.errNotSpecified.format('Project.name'))
    packageId = PackageId(project.groupId, project.name, str(project.version), project.packageExt)
    return project.packageNameStyle().FileName(packageId)
   
#------------------------------------------------------------------------------ 

class install(Target):
  '''TODO: Buduje caly projekt i umieszcza wszystko co potrzebne do jego uruchomienia w bin (default)'''
  dependsOn = ['package']
  
  def Run(self):
    '''TODO: description'''
    # Create install directory (if needed).
    project = GetProject()
    if not os.path.exists(project.installBaseDir):
      Echo('Creating directory: ' + os.path.normpath(project.installBaseDir))
      OS.MakeDirs(project.installBaseDir)
    
    javaClassPath = self.CopyPackage()
    
    if project.type == ProjectType.app:
      javaClassPath += self.CopyDependencies()
      self.CreateStartupScripts(javaClassPath)

    project.installedFiles += javaClassPath
    project.installedFiles += self.CopyAdditionalFiles()
    
    self.CreatePOM()
    
  def CopyPackage(self):
    '''Copy package. TODO: more... '''
    project = GetProject()
    destFileName = os.path.join(project.installBaseDir, os.path.basename(project.packageName))
    if OS.CopyFileIfDiffrent(project.packageName, destFileName, useHash = True, force = True):
      Echo('Installed: ' + destFileName)
    return [destFileName]
  
  def ResolveDependencies(self):
    '''TODO: description'''
    return ResolveDependencies(scope = Dict.Scopes.install)

  def CopyDependencies(self):
    '''Copy dependencies. TODO: more...'''
    project = GetProject()
    filesCopied = self.CopyDependenciesFiles(project.javacClassPath)
    filesCopied += self.CopyDependenciesFiles(self.ResolveDependencies())
    return filesCopied
  
  def CopyDependenciesFiles(self, files):
    '''TODO: description'''
    project = GetProject()
    filesCopied = []
    for name in files:
      if os.path.exists(name) and not os.path.isdir(name):
        destFileName = os.path.join(project.installBaseDir, os.path.basename(name))
        if OS.CopyFileIfDiffrent(name, destFileName, useHash = True, force = True):
          Echo('Installed: ' + destFileName)
        filesCopied.append(destFileName)
    return filesCopied
  
  def CopyAdditionalFiles(self):
    '''TODO: description'''
    project = GetProject()
    installedFiles = []
    for rootDirName, fileName in ExtendedFileSet(project.installAdditionalFiles):
      srcFileName = os.path.join(rootDirName, fileName)
      destFileName = os.path.join(project.installBaseDir, fileName)
      OS.MakeDirs(os.path.dirname(destFileName))
      if OS.CopyFileIfDiffrent(srcFileName, destFileName, useHash = True, force = True):
        Echo('Installed: ' + destFileName)
      installedFiles.append(destFileName)
    return installedFiles
  
  def CreateStartupScripts(self, javaClassPath):
    '''Create shell scripts. TODO: more...'''
    project = GetProject()
    
    javaClassPathStr = ''
    for name in javaClassPath: 
      javaClassPathStr = javaClassPathStr + '${projectHome}/' + os.path.relpath(name, project.installBaseDir) + os.pathsep
    javaClassPathStr = os.path.normpath(javaClassPathStr)
    projectNameInScript = project.name.upper().replace(' ', '_')
    
    from atta.tools import DefaultVarsExpander
    ove = Atta.VarsExpander().SetImpl(DefaultVarsExpander.Expander)
    
    # windows
    with open(self.GetWinStartupScriptTmplFileName(), 'rb') as f:
      scriptName = os.path.join(project.installBaseDir, project.name + '.bat')
      Echo(f, file = scriptName, force = True,
           projectName = projectNameInScript,
           projectHome = '%' + projectNameInScript + '_HOME%',
           mainClass   = project.javaMainClass,
           classPath   = javaClassPathStr)
      project.installedFiles.append(scriptName)
      
    # unix family
    with open(self.GetUnixStartupScriptTmplFileName(), 'rb') as f:
      scriptName = os.path.join(project.installBaseDir, project.name)
      Echo(f, file = scriptName, force = True,
           projectName = projectNameInScript,
           projectHome = '$' + projectNameInScript + '_HOME',
           mainClass   = project.javaMainClass,
           classPath   = javaClassPathStr.replace('\\', '/').replace(';', ':')) 
      if not OS.IsWindows():
        os.chmod(scriptName, stat.S_IEXEC)
      project.installedFiles.append(scriptName)
    
    Atta.VarsExpander().SetImpl(ove)
  
  def GetWinStartupScriptTmplFileName(self):
    '''TODO: description'''
    return Atta.dirName + '/atta/templates/JavaApp.bat.tmpl'
  
  def GetUnixStartupScriptTmplFileName(self):
    '''TODO: description'''
    return Atta.dirName + '/atta/templates/JavaApp.sh.tmpl'

  def CreatePOM(self):
    project = GetProject()
    
    dependencies4POM = [p.AsDependencyInPOM() for p in project.neededPackages]
    dependencies4POM = list(set(dependencies4POM))
    dependencies4POM = '\n'.join(dependencies4POM)
    
    with open(self.GetPOMTmplFileName(), 'rb') as f:
      pomFileName = os.path.join(project.installBaseDir, 
                                 OS.Path.JoinExt(OS.Path.RemoveExt(os.path.basename(project.packageName)), Dict.pom))
      Echo(f, file = pomFileName, force = True,
           groupId = project.groupId,
           artifactId = project.name,
           type = project.packageExt,
           version = str(project.version),
           displayName = project.displayName if len(project.displayName) > 0 else project.name,
           description = project.description,
           url = project.url, 
           dependencies = dependencies4POM,
          )
      project.installedFiles.append(pomFileName)

  def GetPOMTmplFileName(self):  
    return Atta.dirName + '/atta/templates/JavaPOM.tmpl'
  
#------------------------------------------------------------------------------ 

class deploy(Target):
  '''Workflow:
     clean
     full build
     install
     deploy
     tag code
     increase build number
     publish changes made by previous steps
     clean
  '''
  dependsOn = ['install']

  def Prepare(self):
    '''TODO: description'''
    self.UpdateSources()
    GetProject().RunTarget('clean')
    return True
  
  def UpdateSources(self):
    '''Updates working directory from DVCS'''
    project = GetProject()
    if project.dvcs == None:
      return
    self.CheckWorkingDirectory()
    revision = self.GetRevision()
    project.dvcs.UpdateWorkingDirectory(revision)
    if revision != None:
      self.CheckWorkingDirectory()
      
  def CheckWorkingDirectory(self):
    project = GetProject()
    if not project.dvcs.IsWorkingDirectoryClean():
      Echo(Dict.msgDvcsOutputTitle, level = LogLevel.VERBOSE)
      Echo(project.dvcs.output, level = LogLevel.VERBOSE)
      raise AttaError(self, Dict.errDvcsWorkingDirectoryNotClean)

  def GetRevision(self):
    '''We assume that the builds are run on a adequate revision.'''
    return None
  
  def Run(self):
    '''TODO: description'''
    project = GetProject()
    
    packageId = PackageId(project.groupId, project.name, str(project.version), project.packageExt, 
                          timestamp = os.path.getmtime(project.packageName))
    project.deployedFiles = project.Deploy(packageId, project.installedFiles, project.installBaseDir) 
    
    self.TagBuild(self.GetBuildTag())
    self.NextVersion()
    self.Commit(self.GetCommitMessage(), self.GetCommitAuthor())
    
  def GetBuildTag(self):
    return str(GetProject().version)
  
  def TagBuild(self, tag):
    ''''''
    if len(tag) > 0:
      project = GetProject()
      if project.dvcs != None:
        project.dvcs.SetTag(tag)
    
  def NextVersion(self):  
    GetProject().version.NextBuild()
  
  def GetCommitMessage(self):  
    return Dict.msgDvcsNextBuildNumber
  
  def GetCommitAuthor(self):  
    return None
  
  def Commit(self, msg, author):
    if len(msg) > 0:
      project = GetProject()
      if project.dvcs != None:
        project.dvcs.CommitAndPublishAllChanges(msg, author)

  def Finalize(self):
    GetProject().RunTarget('clean', force = True)
    
#------------------------------------------------------------------------------ 

class clean(Target):
  '''TODO: description'''
  def Run(self):
    project = GetProject()
    Delete([project.buildBaseDir, project.installBaseDir], force = True)

#------------------------------------------------------------------------------ 

class help(Target):
  '''TODO: description'''
  def Run(self):
    Echo('Java help...')
        