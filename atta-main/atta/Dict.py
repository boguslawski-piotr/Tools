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
systemPath = 'systemPath'
system     = 'system'
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

dependencies = 'dependencies'
exclusions = 'exclusions'
optional = 'optional'
dependencyStartTag = '<dependency>'
dependencyEndTag   = '</dependency>'

#
# Java related

jar = 'jar'
war = 'war'
pom = 'pom'

#
# Errors

errNotImplemented = 'Not implemented: {0}'
errNotSpecified = 'Not specified: {0}'
errNotEnoughParams = 'Not enough parameters.'
errArchiveImplCantWrite = "The supplied implementation of 'Archive' does not support writing to archive files."

#
# Others
