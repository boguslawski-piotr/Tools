""".. Software projects: Builds Java projects

TODO: description
"""
import os
import stat

from ..repositories.Package import PackageId
from ..repositories import Styles, Maven
from .. import Dict
from ..Activity import Activity

from atta import *

class ProjectType:
  app = 'app'
  jar = Dict.jar
  war = Dict.war

class Setup(Activity):
  """TODO: description"""
  def __init__(self, type = ProjectType.app, **tparams):
    project = self.Project()

    # Java target settings.

    if not project.groupId:
      project.groupId = project.name

    #: DOCTODO: description; available values: see ProjectType
    # TODO: w project jest tez i razem to troche nie gra ze soba - przemyslec
    self.type = type

    #: DOCTODO: description, def repo for dependencies
    self.defaultRepository = tparams.get('defaultRepository', Maven)

    #: DOCTODO: description
    self.srcBaseDir = tparams.get('srcBaseDir', 'src')

    #: DOCTODO: description
    self.buildBaseDir = tparams.get('buildBaseDir', 'build')

    if self.type == ProjectType.app:
      defInstallBaseDir = 'bin'
    else:
      defInstallBaseDir = 'lib'
    #: DOCTODO: description
    self.installBaseDir = tparams.get('installBaseDir', defInstallBaseDir)

    #: DOCTODO: description
    self.archiveBaseDir = tparams.get('archiveBaseDir', 'archive')


    #: DOCTODO: description
    self.javaDirs = [self.srcBaseDir + '/main/java']

    #: DOCTODO: description
    self.javaTestDirs = [self.srcBaseDir + '/test/java']

    #: DOCTODO: description
    self.classDirs = [self.buildBaseDir + '/classes/main']

    #: DOCTODO: description
    self.classTestDirs = [self.buildBaseDir + '/classes/test']


    #: DOCTODO: description
    self.javacClassPathAllowedExts = ['class', 'jar', 'war']

    #: DOCTODO: description
    self.javacClassPath = []

    #: DOCTODO: description
    self.javacSourcePath = []

    #: DOCTODO: description
    self.debug = False

    #: DOCTODO: description
    self.debugLevel = None


    #: DOCTODO: description
    self.packageNameStyle = Styles.Maven

    #: DOCTODO: description
    self.packageExt = self.type
    if self.type == ProjectType.app:
      self.packageExt = Dict.jar

    #: result package file name set in package target DOCTODO: description
    self.packageName = ''

    #: DOCTODO: description
    self.packageAdditionalFiles = []

    #: DOCTODO: description
    self.javaMainClass = tparams.get('mainClass', project.name)


    #: DOCTODO: description
    self.installAdditionalFiles = []

    #: DOCTODO: description
    self.installedFiles = []

    #: DOCTODO: description
    self.neededPackages = []


    #: DOCTODO: description
    self.deployTo = project.deployTo + [
      {
        # Into project subdirectory.
        'repository' : 'atta.repositories.Local',
        'style'      : Styles.ByVersion,
        'rootDirName': self.archiveBaseDir,
      },
    ]

    #: DOCTODO: description
    self.deployedFiles = []

    # Internal settings.

    for p in dir(self):
      if not p.startswith('__'):
        setattr(project, p, getattr(self, p))

    project.targetsMap['prepare'] = 'atta.targets.Java.prepare'
    project.targetsMap['compile'] = 'atta.targets.Java.compile'
    project.targetsMap['package'] = 'atta.targets.Java.package'
    project.targetsMap['install'] = 'atta.targets.Java.install'
    project.targetsMap['deploy'] = 'atta.targets.Java.deploy'
    project.targetsMap['clean'] = 'atta.targets.Java.clean'
    project.targetsMap['help'] = 'atta.targets.Java.help'

    project.defaultTarget = 'help'

#------------------------------------------------------------------------------

def ResolveDependencies(scope):
  project = GetProject()
  files, packages = project.ResolveDependencies(scope = scope, returnPackages = True,
                                                defaultRepository = project.defaultRepository)
  result = []
  if files is not None:
    # Leave only the files that make sense for the Java compiler or/and Java runtime.
    for p in files:
      append = os.path.isdir(p)
      if not append:
        append = OS.Path.Ext(p) in project.javacClassPathAllowedExts
      if append:
        result.append(p)

  if packages:
    project.neededPackages += packages

  return result

#------------------------------------------------------------------------------

class prepare(Target):
  """TODO: description"""
  def Run(self):
    self.PrepareEnvironment()

  def PrepareEnvironment(self):
    """Create the necessary directories."""
    project = self.Project()
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
  """TODO: description"""
  dependsOn = ['prepare']

  def Run(self):
    project = self.Project()
    self.ResolveDependencies()

    i = 0
    for srcDirName in project.javaDirs:
      if not project.classDirs[i] in project.javacClassPath:
        project.javacClassPath.append(project.classDirs[i])

      Javac([srcDirName],
            project.classDirs[i],
            classPath = project.javacClassPath,
            sourcePath = project.javacSourcePath,
            debug = project.debug,
            debugLevel = project.debugLevel,
            cParams = self.JavaCompilerParams(),
            **self.JavacTaskParams())

      if not OS.Path.HasWildcards(srcDirName):
        if not srcDirName in project.javacSourcePath:
          project.javacSourcePath.append(srcDirName)

      if i < len(project.classDirs) - 1:
        i += 1

  def ResolveDependencies(self):
    """TODO: description"""
    project = self.Project()
    project.javacClassPath += ResolveDependencies(scope = Dict.Scopes.compile)

  def JavacTaskParams(self):
    """Additional parameters for Javac task. It must be a dictionary."""
    return {}

  def JavaCompilerParams(self):
    """Additional parameters for Java compiler.
       Passed as cParams to :py:meth:`.IJavaCompiler.Compile` method."""
    return ['-deprecation', '-Xlint']

#------------------------------------------------------------------------------

class package(Target):
  """TODO: description"""
  dependsOn = ['compile']

  def Run(self):
    project = self.Project()
    classDirs = project.classDirs[:]
    self.ExtendClassDirs(classDirs)
    project.packageName = os.path.join(project.buildBaseDir, self.GetPackageName())
    Jar(project.packageName, classDirs, self.GetManifest())

  def ExtendClassDirs(self, classDirs):
    """TODO: description"""
    classDirs.extend(self.Project().packageAdditionalFiles)

  def GetManifest(self):
    """Creates basic manifest."""
    project = self.Project()
    manifest = {
                'Implementation-Title'  : project.name,
                'Implementation-Version': str(project.version),
                'Main-Class'            : project.javaMainClass,
               }
    return manifest

  def GetPackageName(self):
    """Creates package (base) file name."""
    project = self.Project()
    if len(project.name) <= 0:
      raise AttaError(self, Dict.errNotSpecified.format('Project.name'))
    package = PackageId(project.groupId, project.name, str(project.version), project.packageExt)
    return project.packageNameStyle().FileName(package)

#------------------------------------------------------------------------------

class install(Target):
  """TODO: Buduje caly projekt i umieszcza wszystko co potrzebne do jego uruchomienia w bin (default)"""
  dependsOn = ['package']

  def Run(self):
    # Create install directory (if needed).
    project = self.Project()
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
    """Copy package. TODO: more... """
    project = self.Project()
    destFileName = os.path.join(project.installBaseDir, os.path.basename(project.packageName))
    if OS.CopyFileIfDiffrent(project.packageName, destFileName, useHash = True, force = True):
      Echo('Installed: ' + destFileName)
    return [destFileName]

  def ResolveDependencies(self):
    """TODO: description"""
    return ResolveDependencies(scope = Dict.Scopes.runtime)

  def CopyDependencies(self):
    """Copy dependencies. TODO: more..."""
    project = self.Project()
    filesCopied = self.CopyDependenciesFiles(project.javacClassPath)
    filesCopied += self.CopyDependenciesFiles(self.ResolveDependencies())
    return filesCopied

  def CopyDependenciesFiles(self, files):
    """TODO: description"""
    project = self.Project()
    filesCopied = []
    for name in files:
      if os.path.exists(name) and not os.path.isdir(name):
        destFileName = os.path.join(project.installBaseDir, os.path.basename(name))
        if OS.CopyFileIfDiffrent(name, destFileName, useHash = True, force = True):
          Echo('Installed: ' + destFileName)
        filesCopied.append(destFileName)
    return filesCopied

  def CopyAdditionalFiles(self):
    """TODO: description"""
    project = self.Project()
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
    """Create shell scripts. TODO: more..."""
    project = self.Project()

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
           mainClass = project.javaMainClass,
           classPath = javaClassPathStr)
      project.installedFiles.append(scriptName)

    # unix family
    with open(self.GetUnixStartupScriptTmplFileName(), 'rb') as f:
      scriptName = os.path.join(project.installBaseDir, project.name)
      Echo(f, file = scriptName, force = True,
           projectName = projectNameInScript,
           projectHome = '$' + projectNameInScript + '_HOME',
           mainClass = project.javaMainClass,
           classPath = javaClassPathStr.replace('\\', '/').replace(';', ':'))
      if not OS.IsWindows():
        os.chmod(scriptName, stat.S_IEXEC)
      project.installedFiles.append(scriptName)

    Atta.VarsExpander().SetImpl(ove)

  def GetWinStartupScriptTmplFileName(self):
    """TODO: description"""
    return Atta.dirName + '/atta/templates/JavaApp.bat.tmpl'

  def GetUnixStartupScriptTmplFileName(self):
    """TODO: description"""
    return Atta.dirName + '/atta/templates/JavaApp.sh.tmpl'

  def CreatePOM(self):
    project = self.Project()

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

# TODO: run target (dependsOn install)

#------------------------------------------------------------------------------

class deploy(Target):
  """Workflow:
     clean
     full build
     install
     deploy
     tag code
     increase build number
     publish changes made by previous steps
     clean
  """
  dependsOn = ['install']

  def Prepare(self):
    """TODO: description"""
    self.UpdateSources()
    self.Project().RunTarget('clean')
    return True

  def UpdateSources(self):
    """Updates working directory from DVCS"""
    project = self.Project()
    if not project.dvcs:
      return
    self.CheckWorkingDirectory()
    revision = self.GetRevision()
    project.dvcs.UpdateWorkingDirectory(revision)
    if revision:
      self.CheckWorkingDirectory()

  def CheckWorkingDirectory(self):
    project = self.Project()
    if not project.dvcs.IsWorkingDirectoryClean():
      Echo(Dict.msgDvcsOutputTitle, level = LogLevel.VERBOSE)
      Echo(project.dvcs.output, level = LogLevel.VERBOSE)
      raise AttaError(self, Dict.errDvcsWorkingDirectoryNotClean)

  def GetRevision(self):
    """We assume that the builds are run on a adequate revision."""
    return None

  def Run(self):
    """TODO: description"""
    project = self.Project()

    package = PackageId(project.groupId, project.name, str(project.version), project.packageExt,
                        timestamp = os.path.getmtime(project.packageName))
    project.deployedFiles = project.Deploy(project.installBaseDir, project.installedFiles, package)

    self.TagBuild(self.GetBuildTag())
    self.NextVersion()
    self.Commit(self.GetCommitMessage(), self.GetCommitAuthor())

  def GetBuildTag(self):
    return OS.Path.RemoveExt(os.path.basename(self.Project().packageName)).replace(' ', '_')

  def TagBuild(self, tag):
    """"""
    if len(tag) > 0:
      project = self.Project()
      if project.dvcs:
        project.dvcs.SetTag(tag)

  def NextVersion(self):
    self.Project().version.NextBuild()

  def GetCommitMessage(self):
    return Dict.msgDvcsNextBuildNumber

  def GetCommitAuthor(self):
    return None

  def Commit(self, msg, author):
    if len(msg) > 0:
      project = self.Project()
      if project.dvcs != None:
        project.dvcs.CommitAndPublishAllChanges(msg, author)

  def Finalize(self):
    self.Project().RunTarget('clean', force = True)

#------------------------------------------------------------------------------

# TODO: zrobic porzadnie dla major, minor i patch
class nextMinorVersion(Target):
  def Run(self):
    pass

#------------------------------------------------------------------------------

class clean(Target):
  """TODO: description"""
  def Run(self):
    project = self.Project()
    Delete([project.buildBaseDir, project.installBaseDir, '**/*.py?'], force = True)

#------------------------------------------------------------------------------

class help(Target):
  """TODO: description"""
  def Run(self):
    Echo('Java help...')
