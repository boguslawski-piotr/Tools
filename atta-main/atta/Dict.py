"""TODO: description"""

from .tools import OS

class Scopes:
  """TODO: description"""
  compile = 'compile'
  testcompile = 'testcompile'
  runtime = 'runtime'
  testruntime = 'testruntime'

  default = compile

  map2POM = {
             compile     : ['compile'],
             testcompile : ['compile', 'test'],
             runtime     : ['runtime'],
             testruntime : ['runtime', 'test']
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

project = 'project'
target = 'target'

#
# Environment related

attaPropsFileName = 'atta.properties'
defaultBuildFileName = 'build.py'

attaExt = '.atta'
infoExt = '.info'
sha1Ext = 'sha1'

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
timeout = 'timeout'
useCache = 'useCache'
maxRetries = 'maxRetries'
downloadUrl = 'downloadUrl'
url = 'url'
fileNames = 'fileNames'
lifeTime = 'lifeTime'
useFileHashInCheck = 'useFileHashInCheck'

#
# POM releated

systemPath = 'systemPath'
system = 'system'
dependencies = 'dependencies'
dependencyStartTag = '<dependency>'
dependencyEndTag = '</dependency>'
exclusions = 'exclusions'
exclusionsStartTag = '<exclusions>'
exclusionsEndTag = '</exclusions>'
exclusionStartTag = '<exclusion>'
exclusionEndTag = '</exclusion>'
optional = 'optional'
relativePath = 'relativePath'
parent = 'parent'
packaging = 'packaging'
properties = 'properties'
distributionManagement = 'distributionManagement'
bundle = 'bundle'

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
# Common tasks (and others activities) parameters

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

# TODO: jakos rozwiazac te powtorzenia Error...

errNotImplemented = 'Error: Not implemented: {0}'
errNotSpecified = 'Error: Not specified: {0}'
errNotEnoughParams = 'Error: Not enough parameters.'
errInvalidParameterType = 'Error: Invalid type of parameter: %s'
errFileNotExists = 'Error: File: %s does not exists.'
errFileExists = 'Error: File: %s exists.'
errFileOrDirNotExists = 'Error: File or directory: %s does not exists.'
errFileOrDirExists = 'Error: File or directory: %s exists.'
errOSErrorForX = "OS Error: %d, '%s' for: %s"
errPackageNotComplete = 'Error: The definition of the package: %s is not complete.'

errXWhileGettingY = "Error: '%s' while trying to get: %s"
errXWhileGettingYFromZ = "Error: '%s' while trying to get: %s from: %s"
errXWhileGettingStamp = "Error: '%s' while trying to get stamp."
errXWhileSavingY = "Error: '%s' while saving: %s"
errFailedToAssembleX = "Error: Failed to assemble: %s"
errFailedToAssembleXNotFoundY = "Error: Failed to assemble: %s (not found: %s)"

errArchiveImplCantWrite = "Error: The supplied implementation of 'Archive' does not support writing to archive files."

errDvcsWorkingDirectoryNotClean = 'Error: Working directory is not clean.'

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
msgReadingFile = 'Reading file: %s'
msgUploading = 'Uploading: %s'
msgSaving = 'Saving: %s'
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

msgLoadedPropertiesForX = 'Loaded properties for: %s'
msgCollectingDependenciesForX = 'Collecting dependencies for: %s'

msgDvcsRepository = 'Repository: %s'
msgDvcsOutputTitle = 'Output from DVCS:'
msgDvcsNextBuildNumber = 'Next build number'
