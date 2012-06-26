from atta import *
from atta.targets import Java

Project.name = 'JavaExample'
Project.versionName = '0.1'

#print 'in JavaMedium'
#print Project

Java.Setup()

'''
First we have to compile the library 'lib', because the application uses it.
That is why we put the folders at the beginning of the list.
'''
Project.javaDirs.insert(0, Project.srcBaseDir +'/lib/java')
Project.classDirs.insert(0, Project.buildBaseDir + '/classes/lib')

Project.javaDirs += ['*.java']

Project.debug = True
Project.debugLevel = 'vars,lines'

Project.javaMainClass = 'main'

Project.packageAdditionalFiles += ['*.java', '*.py', FileSet(realPaths = False)]

from atta.Dependencies import *

'''
result:

./.repository/com/beust/jcommander/1.26/jcommander-1.26.jar
~/.atta/.repository/commons-net/commons-net/3.1/commons-net-3.1.jar
./../JavaBasic/build/HelloWorld-1.0.jar

'''
Project.ResolveDependencies([{XXX.repository : 'atta.repositories.Maven', XXX.package : 'javax.mail:mail.jar:1.4.5', XXX.putIn : 'atta.repositories.Local'}])

# gets ...
Project.dependsOn += [{
                       XXX.repository: 'atta.repositories.Maven',   # it can be any module with class Repository which implements IRepository
                       XXX.groupId   : 'com.beust',
                       XXX.artifactId: 'jcommander',
                       XXX.version   : '1.26',
                       XXX.type      : 'jar',
                       #or
                       #XXX.package   : 'com.beust:jcommander.jar:1.26',
                       XXX.putIn     : 'atta.repositories.Project', # like repository
                       XXX.dependsOn : [{
                                     XXX.repository : 'atta.repositories.Maven',
                                     XXX.package    : 'commons-net.jar:3.1',
                                     XXX.putIn      : 'atta.repositories.Local',
                                    }],
                                              # and we could continue long ...
                      #XXX.ifNotExists: [{}]
                      }]

Project.dependsOn += [{
                      # Calls Atta project in directory (default: build.py) or with file name specified by: groupId. 
                      XXX.repository: 'atta.repositories.Project',
                      XXX.groupId   : '../JavaBasic',
                      
                      # You can set the following items according to the commentary, or not set, and then Atta will use the default values.
                      
                      # This must be the name or names of the targets separated by spaces.
                      'target'             : 'package',    # default: package
                      
                      # This must be name of project property which may contains: 
                      # string, string path (entries separated by :) or list of strings.
                      # These values will be used in the parameter '-classpath' passed to javac compiler. 
                      'resultIn'           : 'packageName' # default: packageName 
                      }]

Project.dependsOn += [{
                       XXX.repository : 'atta.repositories.Local',
                       XXX.package    : 'javax.mail:mail.jar:1.4.5',
                       XXX.putIn : 'atta.repositories.Project',
                      }]

