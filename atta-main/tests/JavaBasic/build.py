from atta import *
from atta.targets import Java

Project.groupId = 'org.atta'
Project.name = 'JavaBasic'
Project.versionName = '1.0'

Java.Setup(mainClass = 'main')

