from atta import *
from atta.targets import Java

Project.groupId = 'org.atta'
Project.name = 'JavaBasic'
Project.version = '1.0'

Java.Setup(mainClass = 'main')

# This is "fake" dependency. Only for example.
Project.dependsOn = [{
       'repository' : 'atta.repositories.Maven',
       'package'    : 'org.apache.velocity:velocity.jar:1.5'
       }]
