
from atta import *
from atta.targets import Java

#
# Project setup.

Project.groupId = 'org.atta'
#Project.vcs = Git()

from atta.compilers.Strategies import SrcNewerStrategy

def MyVersion(v, event):
  tmplFileName = 'version.java.tmpl'
  javaFileName = 'version.java'

  if event == Version.Events.AfterConfigure:
    if SrcNewerStrategy().RequiresCompile(tmplFileName, javaFileName):
      event = Version.Events.AfterUpdate

  if event == Version.Events.SetPostfix or event == Version.Events.AfterUpdate:
    Filter(tmplFileName, destFile = javaFileName, append = False,
           dataFilters = Project.version.ExpandVars,
           verbose = True)
    OS.Touch('main.java')

Project.version.Configure(impl = Version.ResetBuildStrategy,
                          observers = MyVersion,
                          fileName = 'v.i',
                          # In this project we don't use ${patch} and ${build} version element.
                          format = '${major}.${minor}${postfix}',
                          # More about postfixs you can find in deploy_rc, deploy_release targets below.
                          postfix = '-SNAPSHOT'
                          )

#
Java.Setup(Java.ConsoleApp, mainClass = 'main')

# First we have to compile the library 'lib', because the application uses it.
# That is why we put the folders at the beginning of the list.
Project.javaDirs.insert(0, Project.srcBaseDir + '/lib/java')
Project.classDirs.insert(0, Project.buildBaseDir + '/classes/lib')

# We also have the source files in the root directory.
Project.javaDirs += ['*.java']

#
Project.debug = True
Project.debugLevel = 'vars,lines'

#
Project.packageAdditionalFiles += ['*.java', 'v.i', FileSet(includes = 'src/**/*')]

#
#Project.installAdditionalFiles += ['*.java', '*.py', '../../../Components/AqInternal/**/', FileSet(includes = 'src/**/*')]
Project.installAdditionalFiles += ['*.java', '*.py', FileSet(includes = 'src/**/*')]

#
# Dependencies

# Below dependencies are mostly not real.
# It's only example of power of Atta.

from atta.repositories import Maven
Maven.Repository.resolvers.insert(0, Maven.Repository.Local())
#Maven.Repository.resolvers.append(Maven.Repository.Sonatype())
Maven.Repository.resolvers = [Maven.Repository.Local(), Maven.Repository.Sonatype(), Maven.Repository.Central()]

Project.dependsOn += [{
                       'repository': 'atta.repositories.Maven', # it can be any module with class Repository which inherits from Base.Repository
                       'groupId'   : 'com.beust',
                       'artifactId': 'jcommander',
                       'version'   : '1.26',
                       'type'      : 'jar',
                       #or
                       #'package'   : 'com.beust:jcommander.jar:1.26',
                       'putIn'     : 'atta.repositories.Project', # like repository
                       'dependsOn' : [{
                                     'repository' : 'atta.repositories.Maven',
                                     'package'    : 'commons-net.jar:3.0.1',
                                     'putIn'      : 'atta.repositories.Local',
                                    }],
                                    # and we could continue long ...
                      }]

Project.dependsOn += [{
                      # Calls Atta project in directory (default: build.py) or with file name specified by: project.
                      'repository' : 'atta.repositories.Project',
                      'project'    : '../JavaBasic',
                      'failOnError': True,

                      # You can set the following items according to the commentary,
                      # or not set, and then Atta will use the default values.

                      # This must be the name or names of the targets separated by spaces.
                      'target'     : 'package', # default: package

                      # This must be name (or list of names) of project property(ies) which may contains:
                      # string, string path (entries separated by :) or list of strings.
                      # These values will be used in the parameter '-classpath' passed
                      # to javac if scope is 'compile' (default) or, if scope is 'runtime',
                      # in '-classpath' passed to java.
                      'resultIn'   : ['packageFileName', 'javacClassPath'] # default: packageFileName
                      }]

Project.dependsOn += [{
                      'repository' : '.repositories.Maven',
                      'package'    : 'javax.mail:mail.jar:1.4.5',
                      'scope'      : 'runtime',
                      'putIn'      : {
                                      'repository' : 'atta.repositories.Local',
                                      'style'      : '.repositories.Styles.Flat',
                                     }
                      }]

#Project.dependsOn += [{'package':'bsh.jar:1.3.0','optional':True}]
#Project.dependsOn += ['bsh.jar:1.3.0']

MyMaven = {'repository' : '.repositories.Maven', 'rootDirName' : 'c:\\!!'}
MyMaven2 = Maven.Repository(rootDirName = 'c:\\!!')
class MyMaven3(Maven.Repository): pass

MyPackage = PackageId.FromStr('bsh.jar:1.3.0')
MyPackage.scope = 'runtime'
MyPackage.optional = True

Project.dependsOn += [{'repository' : MyMaven3,
                       'package' : MyPackage,
                       'putIn' : MyMaven2}]

Project.dependsOn += [{
  'repository' : '.repositories.Http',
  'url' : 'http://slinky2.googlecode.com/svn/artifacts/2.1',
  'package' : 'slinky.jar:2.1',
  'fileNames' : ['slinky.jar']
}]


#
# Deploy

p = Properties.Open('deploy.properties')

Project.deployTo += [
#                    {
#                     # into ftp repository
#                     'repository' : 'atta.repositories.Ftp',
#                     'host'       : p.Get('host'),
#                     'rootDirName': p.Get('rootDirName'),
#                     'user'       : p.Get('user'),
#                     'password'   : p.Get('password'),
#                     'useCache'   : False,
#                    },
#                     # into machine local repository
#                     'atta.repositories.Local',
                  ]

#
# Customizing Java targets that come with Atta. It's easy :)
#
# Just define a class that inherits from the class of the Java module.
# No matter on which it will be call level, this class will be used.
# See also example in build2.py.

class deploy(Java.deploy):
  def TagBuild(self, tag):
    if Project.vcs:
      Project.vcs.SetTag(tag, replace = True)

class deploy_rc(deploy):
  def PreparePostfix(self):
    rcN = Project.env.get('N', None)
    if not rcN:
      raise RuntimeError("Please specify the number of 'rc' with parameter '-DN=x' in the command line.")
    self.oldPostfix = Project.version.SetPostfix('-rc%d' % int(rcN))

  def Prepare(self):
    Java.deploy.Prepare(self)
    self.PreparePostfix()
    return True

  def NextVersion(self):
    Project.version.SetPostfix(self.oldPostfix)
    Java.deploy.NextVersion(self)

class deploy_release(deploy_rc):
  def PreparePostfix(self):
    self.oldPostfix = Project.version.SetPostfix('')

  def NextVersion(self):
    Project.version.SetPostfix(self.oldPostfix)
    Project.version.NextMinor()

  def GetCommitMessage(self):
    return 'Next minor version number'

# internal stuff for build2.py

Project.targetsMap['deploy'] = 'build.deploy'
Project.targetsMap['deploy_rc'] = 'build.deploy_rc'
Project.targetsMap['deploy_release'] = 'build.deploy_release'
