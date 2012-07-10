from atta import *
from atta.targets import Java

Project.groupId = 'org.atta'
Project.name = 'JavaBasic'

Java.Setup(mainClass = 'main')

# This is "fake" dependency. Only for example.
Project.dependsOn = [{
       'repository' : 'atta.repositories.Maven',
       'package'    : 'dom4j:dom4j.jar:1.6.1',
       'getOptional': True,
       }]
