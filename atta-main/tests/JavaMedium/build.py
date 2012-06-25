from atta import *
from atta.targets import Java

Project.name = 'JavaExample'
Project.versionName = '0.1'

'''
First we have to compile the library 'lib', because the application uses it.
That is why we put the folders at the beginning of the list.
'''
Java.srcDirs.insert(0, Java.srcBaseDir +'/lib/java')
Java.classDirs.insert(0, Java.classBaseDir + '/lib')

Java.srcDirs += ['main.java']

Java.debug = True
Java.debugLevel = 'vars,lines'

Java.mainClassName = 'main'

'''
TODO: Dependencies...
'''

Java.classPath += ['libs/jcommander-1.26.jar']