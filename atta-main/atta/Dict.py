"""TODO: description"""

from .tools import OS

class Scopes:
  """TODO: description"""
  compile = 'compile'
  testcompile = 'testcompile'
  install = 'install'
  testrun = 'testrun'

  map2POM = {
             compile     : ['compile'],
             testcompile : ['compile'],
             install     : ['compile', 'runtime'],
             testrun     : ['compile', 'runtime']
            }
  '''TODO: description'''

#
# Common

newLine = '\n'
name = 'name'
true = 'true'
false = 'false'
yes = 'yes'
no = 'no'
Or = 'or'

#
# Environment related

defaultBuildFileName = 'build.py'
PATH = 'PATH'

#
# Repositories related

repository = 'repository'
style = 'style'
scope = 'scope'
package = 'package'
groupId = 'groupId'
artifactId = 'artifactId'
version = 'version'
type = 'type'
getOptional = 'getOptional'
dependsOn = 'dependsOn'
putIn = 'putIn'
ifNotExists = 'ifNotExists'
resultIn = 'resultIn'
rootDirName = 'rootDirName'
host = 'host'
port = 'port'
user = 'user'
pasword = 'password'
passive = 'passive'
useCache = 'useCache'
maxRetries = 'maxRetries'

#
# POM releated

systemPath = 'systemPath'
system = 'system'
dependencies = 'dependencies'
dependencyStartTag = '<dependency>'
dependencyEndTag = '</dependency>'
exclusions = 'exclusions'
optional = 'optional'
relativePath = 'relativePath'
parent = 'parent'
packaging = 'packaging'
properties = 'properties'
project = 'project'

#
# Java related

JAVA_HOME = 'JAVA_HOME'
JAVAC_EXE = 'javac'
JAVAC_EXE_IN_JAVA_HOME = 'bin/javac'
if OS.IsWindows():
  JAVAC_EXE_IN_PATH = 'javac.exe'
else:
  JAVAC_EXE_IN_PATH = 'javac.exe'

basicManifest = 'Manifest-Version: 1.0\nAtta-Version: %s %s\n'
manifestFileName = 'META-INF/MANIFEST.MF'

jar = 'jar'
war = 'war'
pom = 'pom'

#
# Dvcs related

GIT_HOME = 'GIT_HOME'
GIT_EXE = 'git'
if OS.IsWindows():
  GIT_EXE_IN_PATH = 'git.cmd:git.exe:git.bat'
else:
  GIT_EXE_IN_PATH = GIT_EXE

#
# Common tasks (and others activites) parameters

paramLevel = 'level'
paramQuiet = 'quiet'
paramFailOnError = 'failOnError'
paramLogOutput = 'logOutput'
paramForce = 'force'
paramClassPath = 'classPath'
paramSourcePath = 'sourcePath'
paramDestDirName = 'destDirName'
paramDestFile = 'destFile'
paramDirName = 'dirName'

#
# Errors

errNotImplemented = 'Not implemented: {0}'
errNotSpecified = 'Not specified: {0}'
errNotEnoughParams = 'Not enough parameters.'
errFileNotExists = 'File: %s does not exists.'
errFileExists = 'File: %s exists.'
errFileOrDirNotExists = 'File or directory: %s does not exists.'
errFileOrDirExists = 'File or directory: %s exists.'
errOSErrorForX = "OS error: %d, '%s' for: %s"
errException = "Exception: '%s'"

errXWhileGettingYFromZ = "Error '%s' while trying to get: %s from: %s"
errXWhileGettingTimestamp = "Error '%s' while trying to get timestamp."

errArchiveImplCantWrite = "The supplied implementation of 'Archive' does not support writing to archive files."

errDvcsWorkingDirectoryNotClean = 'Working directory is not clean.'

#
# Messages

msgDumpParameters = '\n*** Parameters:'
msgChecking = 'Checking: {0}'
msgCheckingWithX = 'Checking: {0} with: {1}'
msgCreating = 'Creating: {0}'
msgDelDirectory = 'Deleting directory: %s'
msgExitCode = 'exit code: {0}'
msgFile = 'File: %s'
msgDirectory = 'Directory: %s'
msgFrom = 'From: %s'
msgDownloading = 'Downloading: %s'
msgDownloadingFile = 'Downloading file: %s'
msgUploading = 'Uploading: %s'
msgSavingFile = 'Saving file: %s'
msgReturns = 'Returns: %s'
msgSendingXToY = 'Sending: %s to: %s'
msgProcessing = 'Processing: %s'
msgProcessingXToY = 'Processing: %s to: %s'
msgSkipped = 'Skipped: %s'
msgProcessedAndSkipped = 'Processed %d file(s), skipped %d file(s).'
msgCopyingXToY = 'Copying: %s to: %s'
msgCopiedAndSkipped = 'Copied %d file(s), skipped %d file(s).'
msgMovingXToY = 'Moving: %s to: %s'
msgMovedAndSkipped = 'Moved %d file(s), skipped %d file(s).'
msgDeletedDirsAndFiles = 'Deleted %d director(ies)(y), %d file(s)'

msgWithManifest = 'with manifest:'
msgWithFiles = 'with files:'
msgXfromY = '%s from: %s'
msgXtoY = '%s to: %s'
msgChangedFromXToYInZ = 'Changed from: %s to: %s in: %s'
msgNoneHaveBeenAdded = 'To: %s none have been added.'

msgNothingToCompile = 'Nothing to compile in: {0}'
msgCompilingTo = 'Compiling %d source file(s) to: %s'

msgLoadingPropertiesForX = 'Loading properties for: %s'
msgCollectingDependenciesForX = 'Collecting dependencies for: %s'

msgDvcsRepository = 'Repository: %s'
msgDvcsOutputTitle = 'Output from DVCS:'
msgDvcsNextBuildNumber = 'Next build number'
