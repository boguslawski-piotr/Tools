'''TODO: description'''

class Scopes:
  '''TODO: description'''
  compile     = 'compile'
  testcompile = 'testcompile'
  install     = 'install'
  testrun     = 'testrun'
  
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

#
#

defaultBuildFileName = 'build.py'

#
# Repositories related

repository = 'repository'
style      = 'style'
scope      = 'scope'
package    = 'package'
groupId    = 'groupId'
artifactId = 'artifactId'
version    = 'version'
type       = 'type'
getOptional= 'getOptional'
dependsOn  = 'dependsOn'
putIn      = 'putIn'
ifNotExists= 'ifNotExists'
resultIn   = 'resultIn'
rootDir    = 'rootDir'
host       = 'host'
port       = 'port'
user       = 'user'
pasword    = 'password'
passive    = 'passive'
useCache   = 'useCache'
maxRetries = 'maxRetries'

#
# POM releated

systemPath = 'systemPath'
system = 'system'
dependencies = 'dependencies'
dependencyStartTag = '<dependency>'
dependencyEndTag   = '</dependency>'
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

basicManifest = 'Manifest-Version: 1.0\nAtta-Version: %s %s\n'
manifestFileName = 'META-INF/MANIFEST.MF'

jar = 'jar'
war = 'war'
pom = 'pom'

#
# Common tasks (and others activites) parameters

paramLogOutput = 'logOutput'

paramClassPath = 'classPath'
paramSourcePath = 'sourcePath'

#
# Errors

errNotImplemented = 'Not implemented: {0}'
errNotSpecified = 'Not specified: {0}'
errNotEnoughParams = 'Not enough parameters.'
errFileNotExists = 'File: %s does not exists.'
errOSErrorForX = "OS error: %d, '%s' for: %s"

errXWhileGettingYFromZ = "Error '%s' while trying to get: %s from: %s"
errXWhileGettingTimestamp = "Error '%s' while trying to get timestamp."

errArchiveImplCantWrite = "The supplied implementation of 'Archive' does not support writing to archive files."

errDvcsWorkingDirectoryNotClean = 'Working directory is not clean.'

#
# Others

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

msgWithManifest = 'with manifest:'
msgWithFiles = 'with files:'
msgXfromY = '  %s from: %s'
msgChangedFromXToYInZ = 'Changed from: %s to: %s in: %s'
msgNoneHaveBeenAdded = 'To: %s none have been added.'

msgNothingToCompile = 'Nothing to compile in: {0}'
msgCompilingTo = 'Compiling %d source file(s) to: %s'

msgGettingProperties = 'Loading properties from: %s'

msgDvcsRepository = 'Repository: %s'
msgDvcsOutputTitle = 'Output from DVCS:'
msgDvcsNextBuildNumber = 'Next build number'
