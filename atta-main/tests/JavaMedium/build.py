from atta import *
from atta.targets import Java

'''
Project setup.
'''

Project.groupId = 'org.atta'
Project.name = 'JavaMedium'
Project.versionName = '0.1'

Java.Setup(Java.ProjectType.consoleApp)

'''
First we have to compile the library 'lib', because the application uses it.
That is why we put the folders at the beginning of the list.
'''
Project.javaDirs.insert(0, Project.srcBaseDir +'/lib/java')
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
Project.javaMainClass = 'main'

'''
'''
Project.packageAdditionalFiles += ['*.java', '*.py', FileSet(includes = 'src/**/*', realPaths = False)]

'''
'''
#Project.installAdditionalFiles += ['*.java', '*.py', r'../../../Components/AqInternal/**/', FileSet(includes = 'src/**/*', realPaths = False)]

'''
Customizing Java targets that come with Atta. It's easy :)

Just define a class that inherits from the class of the Java module.
No matter on which it will be call level, this class will be used.
'''

class prepare(Java.prepare):
  def ResolveDependencies(self):
    Echo('My ResolveDependencies')
    Java.prepare.ResolveDependencies(self)

class compile(Java.compile):
  def Run(self):
    Echo('My compile')
    Java.compile.Run(self)

'''
Deploy
'''

from atta.repositories.Styles import Flat
    
class MyStylePackageId(Flat):
  def DirName(self, packageId):
    return '%s' % (str(packageId.version))

Project.deployTo = [
                    {
                     # into ftp repository
                     'repository' : 'atta.repositories.Ftp',
                     'host'       : 'w2.automapa.pl',
                     'rootDir'    : 'Exchange/Piotrb',
                     'user'       : 'piotrb',
                     'password'   : 'vi-65-dze',
                    },
#                    {
#                     # into subdirectory archive
#                     'repository' : 'atta.repositories.Local',
#                     'style'      : 'build.MyStylePackageId',
#                     #'style'      : 'atta.repositories.Styles.Flat',
#                     'rootDir'    : 'archive',
#                    },
#                    {
#                     # into machine local repository
#                     'repository' : 'atta.repositories.Local',
#                    }
                    ]        
'''
Dependencies
------------

Przyklad jest troche wydumany, ale ma pokazac rozne mozliwosci...

Result:

~/.atta/.repository/javax/mail/mail/1.4.5/mail-1.4.5.jar
./.repository/com/beust/jcommander/1.26/jcommander-1.26.jar
~/.atta/.repository/commons-net/commons-net/3.1/commons-net-3.1.jar
./../JavaBasic/build/HelloWorld-1.0.jar
./.repository/javax/mail/mail/1.4.5/mail-1.4.5.jar

PROBLEM (do rozwiazania):
pobieram z Maven wrzucajac do Ftp
Ftp zwraca pliki, ale one sa nie do uzycia !
???
'''

#test = [
#        {
#         'repository' : 'atta.repositories.Ftp',
#         'host'       : 'w2.automapa.pl',
#         'rootDir'    : 'Exchange/Piotrb',
#         'user'       : 'piotrb',
#         'password'   : 'vi-65-dze',
#         'package'    : 'org.atta:JavaMedium.jar:0.1',
#         'putIn'      : 'atta.repositories.Project',
#        },
#        ] 

test = [{
       'repository' : 'atta.repositories.Maven',
       'package'    : 'commons-net.jar:3.1',
       'putIn' :
          {
           'repository' : 'atta.repositories.Ftp',
           'style'      : 'atta.repositories.Styles.Flat',
           'host'       : 'w2.automapa.pl',
           'rootDir'    : 'Exchange/Piotrb',
           'user'       : 'piotrb',
           'password'   : 'vi-65-dze',
#           'package'    : 'org.atta:JavaMedium.jar:0.1',
#           'putIn'      : 'atta.repositories.Project',
          },
        }] 

r = Project.ResolveDependencies(test)
#print r

# gets ...
Project.dependsOn += [{
                       'repository': 'atta.repositories.Maven',   # it can be any module with class Repository which inherits from ARepository
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
                      
                      # You can set the following items according to the commentary, or not set, and then Atta will use the default values.
                      
                      # This must be the name or names of the targets separated by spaces.
                      'target'             : 'package',    # default: package
                      
                      # This must be name of project property which may contains: 
                      # string, string path (entries separated by :) or list of strings.
                      # These values will be used in the parameter '-classpath' passed to javac compiler. 
                      'resultIn'           : 'packageName' # default: packageName 
                      }]

Project.dependsOn += [{
                       'repository' : 'atta.repositories.Local',
                       'style'      : 'atta.repositories.Styles.Flat',
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

