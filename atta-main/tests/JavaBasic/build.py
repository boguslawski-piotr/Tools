from atta import *
from atta.targets import Java

Project.name = 'HelloWorld'
Project.versionName = '1.0'

#print 'in JavaBasic'
#print Project

Java.Setup(mainClass = 'main')

