
from atta import *
from atta.targets import Java

'''
Project setup.
'''

Project.groupId = 'org.atta'
Project.name = 'JavaMedium'
#Project.dvcs = Git()
p = Properties.Open('deploy.properties')

from atta.compilers.Strategies import SrcNewerStrategy
from atta.tools.Strategies import VersionResetBuildStrategy

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

Project.version.Configure(impl = VersionResetBuildStrategy,
                           observers = MyVersion,
                           fileName = 'v.i',
                           # In this project we don't use ${patch} and ${build} version element.
                           format = '${major}.${minor}${postfix}',
                           # More about postfixs you can find in deploy_rc, deploy_release targets below.
                           postfix = '-SNAPSHOT'

                           # TODO: more formats for file: ini, prop, py, etc.
                          )

'''
'''
Java.Setup(Java.ProjectType.app, mainClass = 'main')

'''
First we have to compile the library 'lib', because the application uses it.
That is why we put the folders at the beginning of the list.
'''
Project.javaDirs.insert(0, Project.srcBaseDir + '/lib/java')
Project.classDirs.insert(0, Project.buildBaseDir + '/classes/lib')

'''
We also have the source files in the root directory.
'''
Project.javaDirs += ['*.java']

'''
'''
Project.debug = True
Project.debugLevel = 'vars,lines'

'''
'''
Project.packageAdditionalFiles += ['*.java', 'v.i', FileSet(includes = 'src/**/*')]

'''
'''
#Project.installAdditionalFiles += ['*.java', '*.py', r'../../../Components/AqInternal/**/', FileSet(includes = 'src/**/*', realPaths = False)]

'''
Dependencies
------------
'''

# Below dependencies are mostly not real. 
# It's only example of power of Atta.

Project.dependsOn += [{
                       'repository': 'atta.repositories.Maven', # it can be any module with class Repository which inherits from ARepository
                       'groupId'   : 'com.beust',
                       'artifactId': 'jcommander',
                       'version'   : '1.26',
                       'type'      : 'jar',
                       #or
                       #'package'   : 'com.beust:jcommander.jar:1.26',
                       'putIn'     : 'atta.repositories.Project', # like repository
                       'dependsOn' : [{
                                     'repository' : 'atta.repositories.Maven',
                                     'package'    : 'commons-net.jar:3.1',
                                     'putIn'      : 'atta.repositories.Local',
                                    }],
                                    # and we could continue long ...
                      }]

Project.dependsOn += [{
                      # Calls Atta project in directory (default: build.py) or with file name specified by: groupId. 
                      'repository': 'atta.repositories.Project',
                      'groupId'   : '../JavaBasic',

                      # You can set the following items according to the commentary, 
                      # or not set, and then Atta will use the default values.

                      # This must be the name or names of the targets separated by spaces.
                      'target'    : 'package', # default: package

                      # This must be name (or list of names) of project property(ies) which may contains: 
                      # string, string path (entries separated by :) or list of strings.
                      # These values will be used in the parameter '-classpath' passed to javac compiler. 
                      'resultIn'  : ['packageName', 'javacClassPath'] # default: packageName 
                      }]

Project.dependsOn += [{
                       'repository' : 'atta.repositories.Local',
                       'style'      : 'atta.repositories.Styles.Flat',
                       'scope'      : 'install',
                       'package'    : 'javax.mail:mail.jar:1.4.5',
                       'ifNotExists': [{
                                        'repository' : 'atta.repositories.Maven',
                                        'package'    : 'javax.mail:mail.jar:1.4.5',
                                        'putIn'      : {
                                                        'repository' : 'atta.repositories.Local',
                                                        'style'      : 'atta.repositories.Styles.Flat',
                                                       }
                                       }]
                      }]

'''
Deploy
'''

from atta.repositories import Styles

class MyStyle(Styles.Flat):
  def DirName(self, packageId):
    return '%s' % (str(packageId.version))

Project.deployTo = [
#                    {
#                     # into ftp repository
#                     'repository' : 'atta.repositories.Ftp',
#                     'host'       : p.Get('host'),
#                     'rootDirName': p.Get('rootDirName'),
#                     'user'       : p.Get('user'),
#                     'password'   : p.Get('password'),
#                     'useCache'   : False,
#                    },
#                    {
#                     # into machine local repository
#                     'repository' : 'atta.repositories.Local',
#                    },
                    {
                     # into project subdirectory archive
                     'repository' : 'atta.repositories.Local',
                     'style'      : MyStyle,
                     'rootDirName': 'archive',
                    },
                  ]

'''
Customizing Java targets that come with Atta. It's easy :)

Just define a class that inherits from the class of the Java module.
No matter on which it will be call level, this class will be used.
See also example in build2.py.
'''

class deploy(Java.deploy):
  def TagBuild(self, tag):
    if Project.dvcs != None:
      Project.dvcs.SetTag(tag, replace = True)

class deploy_rc(deploy):
  def PreparePostfix(self):
    rcN = Project.env.get('N', None)
    if rcN == None or rcN == '':
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

'''
# for build2.py
'''

Project.targetsMap['deploy'] = 'build.deploy'
Project.targetsMap['deploy_rc'] = 'build.deploy_rc'
Project.targetsMap['deploy_release'] = 'build.deploy_release'
