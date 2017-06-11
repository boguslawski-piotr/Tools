""".. Software projects: Builds Java projects

TODO: description
"""
import os
import stat

from ..repositories import Styles, Maven
from .. import Atta, AttaError, LogLevel, Dict, Target, Echo, Delete, OS, Copy, Exec
from ..Activity import Activity

from ..tasks import Javac, Jar
Javac = Javac.Javac
Jar = Jar.Jar

#: DOCTODO: description
ConsoleApp = 'capp'

#: DOCTODO: description
Library = Dict.jar

#: DOCTODO: description
WebApp = Dict.war

class Setup(Activity):
  """TODO: description"""

  # Internal: the type of project being built.
  _projectType = ConsoleApp

  def __init__(self, projectType = ConsoleApp, **tparams):
    project = self.Project

    # Java target settings.

    if not project.groupId: project.groupId = project.name
    Setup._projectType = projectType

    #: DOCTODO: description
    self.srcBaseDir = tparams.get('srcBaseDir', 'src')

    #: DOCTODO: description
    self.buildBaseDir = tparams.get('buildBaseDir', 'build')

    if Setup._projectType == ConsoleApp:
      defInstallBaseDirName = 'bin'
    else:
      defInstallBaseDirName = 'lib'
    #: DOCTODO: description
    self.installBaseDir = tparams.get('installBaseDir', defInstallBaseDirName)

    #: DOCTODO: description
    self.archiveBaseDir = tparams.get('archiveBaseDir', 'archive')

    #: DOCTODO: description, def repo for dependencies
    self.defaultRepository = tparams.get('defaultRepository', Maven)


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
    if Setup._projectType == WebApp:
      self.type = Dict.war
    else:
      self.type = Dict.jar

    #: result package file name set in package target DOCTODO: description
    self.packageFileName = ''

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
    project.targetsMap['run'] = 'atta.targets.Java.run'
    project.targetsMap['deploy'] = 'atta.targets.Java.deploy'
    project.targetsMap['clean'] = 'atta.targets.Java.clean'
    project.targetsMap['help'] = 'atta.targets.Java.help'

    project.defaultTarget = 'help'

#------------------------------------------------------------------------------

def _ResolveDependencies(project, scope):
  files, packages = project.ResolveDependencies(scope = scope, returnPackages = True,
                                                defaultRepository = project.defaultRepository)
  result = []
  if files:
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
    project = self.Project
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

  def Prepare(self):
    self.ResolveDependencies()
    return True

  def ResolveDependencies(self):
    """TODO: description"""
    project = self.Project
    project.javacClassPath += _ResolveDependencies(self.Project, scope = Dict.Scopes.compile)

  def Run(self):
    project = self.Project

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
    project = self.Project
    classDirs = project.classDirs[:]
    self.ExtendClassDirs(classDirs)
    project.packageFileName = os.path.join(project.buildBaseDir, self.GetPackageName())
    Jar(project.packageFileName, classDirs, self.GetManifest())

  def ExtendClassDirs(self, classDirs):
    """TODO: description"""
    classDirs.extend(self.Project.packageAdditionalFiles)

  def GetManifest(self):
    """Creates basic manifest."""
    project = self.Project
    manifest = {
                'Implementation-Title'  : project.name,
                'Implementation-Version': str(project.version),
                'Main-Class'            : project.javaMainClass,
               }
    return manifest

  def GetPackageName(self):
    """Creates package (base) file name."""
    project = self.Project
    if not project.name:
      raise AttaError(self, Dict.errNotSpecified.format('Project.name'))
    package = project.CreatePackage()
    return package.AsFileName(project.packageNameStyle)
    #return project.packageNameStyle().FileName(package)

#------------------------------------------------------------------------------

class install(Target):
  """TODO: Buduje caly projekt i umieszcza wszystko co potrzebne do jego uruchomienia w bin (default)"""
  dependsOn = ['package']

  def Run(self):
    # Create install directory (if needed).
    project = self.Project
    if not os.path.exists(project.installBaseDir):
      Echo('Creating directory: ' + os.path.normpath(project.installBaseDir))
      OS.MakeDirs(project.installBaseDir)

    javaClassPath = self.CopyPackage()

    if Setup._projectType == ConsoleApp:
      javaClassPath += self.CopyDependencies()
      self.CreateStartupScripts(javaClassPath)

    project.installedFiles += javaClassPath
    project.installedFiles += self.CopyAdditionalFiles()

    self.CreatePOM()

  def CopyPackage(self):
    """Copy package. TODO: more... """
    c = Copy(self.Project.packageFileName, destDirName = self.Project.installBaseDir, useHash = True, force = True)
    return [dfn for sfn, dfn in c.processedFiles + c.skippedFiles]

  def ResolveDependencies(self):
    """TODO: description"""
    return _ResolveDependencies(self.Project, scope = Dict.Scopes.runtime)

  def CopyDependencies(self):
    """Copy dependencies. TODO: more..."""
    filesCopied = self.CopyDependenciesFiles(self.Project.javacClassPath)
    filesCopied += self.CopyDependenciesFiles(self.ResolveDependencies())
    return filesCopied

  def CopyDependenciesFiles(self, files):
    """TODO: description"""
    filesToCopy = [name for name in files if os.path.exists(name) and not os.path.isdir(name)]
    c = Copy(filesToCopy, destDirName = self.Project.installBaseDir, useHash = True, force = True)
    return [dfn for sfn, dfn in c.processedFiles + c.skippedFiles]

  def CopyAdditionalFiles(self):
    """TODO: description"""
    c = Copy(self.Project.installAdditionalFiles, destDirName = self.Project.installBaseDir, useHash = True, force = True)
    return [dfn for sfn, dfn in c.processedFiles + c.skippedFiles]

  def CreateStartupScripts(self, javaClassPath):
    """Create shell scripts. TODO: more..."""
    project = self.Project

    javaClassPathStr = ''
    for name in javaClassPath:
      javaClassPathStr = javaClassPathStr + '${projectHome}/' + os.path.relpath(name, project.installBaseDir) + os.pathsep
    javaClassPathStr = os.path.normpath(javaClassPathStr)
    projectNameInScript = project.name.upper().replace(' ', '_')

    from ..tools import DefaultVarsExpander
    ove = Atta.VarsExpander().SetImpl(DefaultVarsExpander.Expander)

    # windows
    with open(self.GetWinStartupScriptTmplFileName(), 'rb') as f:
      scriptFileName = os.path.join(project.installBaseDir, project.name + '.bat')
      Echo(f, file = scriptFileName, force = True,
           projectName = projectNameInScript,
           projectHome = '%' + projectNameInScript + '_HOME%',
           mainClass = project.javaMainClass,
           classPath = javaClassPathStr)
      project.installedFiles.append(scriptFileName)

    # unix family
    with open(self.GetUnixStartupScriptTmplFileName(), 'rb') as f:
      scriptFileName = os.path.join(project.installBaseDir, project.name)
      Echo(f, file = scriptFileName, force = True,
           projectName = projectNameInScript,
           projectHome = '$' + projectNameInScript + '_HOME',
           mainClass = project.javaMainClass,
           classPath = javaClassPathStr.replace('\\', '/').replace(';', ':'))
      if not OS.IsWindows():
        os.chmod(scriptFileName, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
      project.installedFiles.append(scriptFileName)

    Atta.VarsExpander().SetImpl(ove)

  def GetWinStartupScriptTmplFileName(self):
    """TODO: description"""
    return Atta.dirName + '/atta/templates/JavaApp.bat.tmpl'

  def GetUnixStartupScriptTmplFileName(self):
    """TODO: description"""
    return Atta.dirName + '/atta/templates/JavaApp.sh.tmpl'

  def CreatePOM(self):
    project = self.Project

    dependencies4POM = [p.AsDependencyInPOM() for p in project.neededPackages]
    dependencies4POM = list(set(dependencies4POM))
    dependencies4POM = '\n'.join(dependencies4POM)

    with open(self.GetPOMTmplFileName(), 'rb') as f:
      pomFileName = os.path.join(project.installBaseDir,
                                 OS.Path.JoinExt(OS.Path.RemoveExt(os.path.basename(project.packageFileName)), Dict.pom))
      Echo(f, file = pomFileName, force = True,
           groupId = project.groupId,
           artifactId = project.name,
           type = project.type,
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

class run(Target):
  dependsOn = ['install']
  def Run(self):
    project = self.Project
    if Setup._projectType == ConsoleApp:
      scriptFileName = os.path.join(project.installBaseDir, project.name)
      Exec(scriptFileName + '${bat}', project.targetsParameters['run'])
      # you can: atta "run param1 param2 ..."

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
    self.Project.RunTarget('clean')
    return True

  def UpdateSources(self):
    """Updates working directory from DVCS"""
    project = self.Project
    if not project.vcs:
      return
    self.CheckWorkingDirectory()
    revision = self.GetRevision()
    project.vcs.UpdateWorkingDirectory(revision)
    if revision:
      self.CheckWorkingDirectory()

  def CheckWorkingDirectory(self):
    project = self.Project
    if not project.vcs.IsWorkingDirectoryClean():
      Echo(Dict.msgDvcsOutputTitle, level = LogLevel.VERBOSE)
      Echo(project.vcs.output, level = LogLevel.VERBOSE)
      raise AttaError(self, Dict.errDvcsWorkingDirectoryNotClean)

  def GetRevision(self):
    """We assume that the builds are run on a adequate revision."""
    return None

  def Run(self):
    """TODO: description"""
    project = self.Project

    package = project.CreatePackage()
    package.stamp = OS.FileTimestamp(project.packageFileName)
    project.deployedFiles = project.Deploy(project.installBaseDir, project.installedFiles, package)

    self.TagBuild(self.GetBuildTag())
    self.NextVersion()
    self.Commit(self.GetCommitMessage(), self.GetCommitAuthor())

  def GetBuildTag(self):
    return OS.Path.RemoveExt(os.path.basename(self.Project.packageFileName)).replace(' ', '_')

  def TagBuild(self, tag):
    """"""
    if len(tag) > 0:
      project = self.Project
      if project.vcs:
        project.vcs.SetTag(tag)

  def NextVersion(self):
    self.Project.version.NextBuild()

  def GetCommitMessage(self):
    return Dict.msgDvcsNextBuildNumber

  def GetCommitAuthor(self):
    return None

  def Commit(self, msg, author):
    if len(msg) > 0:
      project = self.Project
      if project.vcs:
        project.vcs.CommitAndPublishAllChanges(msg, author)

  def Finalize(self):
    self.Project.RunTarget('clean', force = True)

#------------------------------------------------------------------------------

# TODO: zrobic porzadnie dla major, minor i patch
class nextMinorVersion(Target):
  def Run(self):
    pass

#------------------------------------------------------------------------------

class clean(Target):
  """TODO: description"""
  def Run(self):
    project = self.Project
    Delete([project.buildBaseDir, project.installBaseDir, '**/*.py?'], force = True)

#------------------------------------------------------------------------------

class help(Target):
  """TODO: description"""
  def Run(self):
    Echo('Java help...')
